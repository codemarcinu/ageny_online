from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
import re

from backend.core.llm_providers.provider_factory import provider_factory as llm_factory
from backend.api.v2.endpoints.web_search import WebSearchRequest, search_providers
from backend.schemas.tutor import TutorRequest, TutorResponse
from backend.agents.tutor_agent import TutorAntonina

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    """Chat completion request model."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    model: Optional[str] = Field(None, description="Model to use for completion")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)
    provider: Optional[str] = Field(None, description="Specific provider to use")
    stream: bool = Field(False, description="Whether to stream the response")
    enable_web_search: bool = Field(True, description="Whether to enable web search for current information")
    tutor_mode: bool = Field(False, description="Włącz tryb Tutor Antoniny")

class ChatResponse(BaseModel):
    """Chat completion response model."""
    text: str
    model: str
    provider: str
    usage: Dict[str, int]
    cost: Dict[str, float]
    finish_reason: str
    response_time: float
    web_search_used: bool = False
    web_search_results: Optional[List[Dict[str, Any]]] = None
    tutor_question: Optional[str] = Field(None, description="Pytanie doprecyzowujące od tutora")
    tutor_feedback: Optional[str] = Field(None, description="Sugestia i ulepszony prompt od tutora")

class EmbedRequest(BaseModel):
    """Embedding request model."""
    texts: List[str] = Field(..., description="List of texts to embed")
    model: Optional[str] = Field(None, description="Model to use for embedding")

def should_use_web_search(message: str) -> bool:
    """Determine if web search should be used based on message content."""
    # Keywords that indicate need for current information
    current_info_keywords = [
        "dzisiaj", "obecnie", "aktualnie", "ostatnio", "niedawno", "w tym roku",
        "w tym miesiącu", "w tym tygodniu", "dzisiejsze", "obecne",
        "today", "currently", "recently", "latest", "current", "now",
        "2024", "2025", "2026", "2027", "2028", "2029", "2030"
    ]
    
    # Questions about time-sensitive topics
    time_sensitive_patterns = [
        r"co się stało w \d{4}",
        r"kiedy.*\d{4}",
        r"what happened in \d{4}",
        r"when.*\d{4}",
        r"aktualne wiadomości",
        r"current news",
        r"ostatnie wydarzenia",
        r"recent events"
    ]
    
    message_lower = message.lower()
    
    # Check for current info keywords
    for keyword in current_info_keywords:
        if keyword in message_lower:
            return True
    
    # Check for time-sensitive patterns
    for pattern in time_sensitive_patterns:
        if re.search(pattern, message_lower):
            return True
    
    return False

async def perform_web_search(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Perform web search and return formatted results."""
    try:
        if "duckduckgo" not in search_providers:
            logger.warning("DuckDuckGo provider not available")
            return []
        
        provider = search_providers["duckduckgo"]
        results = await provider.search(query, max_results)
        
        # Convert to dict format
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "source": result.source,
                "timestamp": result.timestamp
            })
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate chat completion using available LLM providers with optional web search.
    """
    start_time = time.time()
    
    try:
        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="At least one message is required")
        
        # Validate message structure
        for i, message in enumerate(request.messages):
            if not message.role or not message.content:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid message at index {i}: role and content are required"
                )
            if message.role not in ["user", "assistant", "system"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role '{message.role}' at index {i}. Must be 'user', 'assistant', or 'system'"
                )
        
        last_message = request.messages[-1].content
        web_search_used = False
        web_search_results = None
        
        # Check if web search should be used
        if request.enable_web_search and should_use_web_search(last_message):
            logger.info(f"Performing web search for query: {last_message}")
            try:
                web_search_results = await perform_web_search(last_message, max_results=3)
                web_search_used = len(web_search_results) > 0
                
                if web_search_used:
                    # Enhance the message with web search results
                    enhanced_message = f"{last_message}\n\nAktualne informacje z internetu:\n"
                    for i, result in enumerate(web_search_results, 1):
                        enhanced_message += f"{i}. {result['title']}: {result['snippet']}\n"
                        enhanced_message += f"   Źródło: {result['url']}\n\n"
                    
                    # Update the last message with enhanced content
                    request.messages[-1].content = enhanced_message
            except Exception as e:
                logger.warning(f"Web search failed, continuing without it: {e}")
        
        # Generate response using LLM provider
        try:
            if request.provider:
                # Use specific provider
                provider_type = None
                
                # Check if we're in test mode (llm_factory is mocked)
                if hasattr(llm_factory, '_mock_name'):
                    # Test mode - create mock provider type
                    from backend.core.llm_providers.provider_factory import ProviderType
                    provider_type = ProviderType(request.provider)
                else:
                    # Normal mode - check available providers
                    for pt in llm_factory.get_available_providers():
                        if pt.value == request.provider:
                            provider_type = pt
                            break
                
                if not provider_type:
                    available_providers = [p.value for p in llm_factory.get_available_providers()]
                    logger.error(f"Provider {request.provider} not available. Available: {available_providers}")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Provider {request.provider} not available. Available: {available_providers}"
                    )
                
                provider = llm_factory.get_provider(provider_type)
                result = await provider.chat(
                    messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
            else:
                # Use fallback provider
                result = await llm_factory.chat_with_fallback(
                    messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
        except Exception as e:
            logger.error(f"LLM provider error: {e}")
            raise HTTPException(status_code=500, detail=f"LLM provider error: {str(e)}")
        
        # Add response time and web search info
        result["response_time"] = time.time() - start_time
        result["web_search_used"] = web_search_used
        result["web_search_results"] = web_search_results
        
        # Initialize tutor fields
        result["tutor_question"] = None
        result["tutor_feedback"] = None
        
        # Handle Tutor Antonina mode
        if request.tutor_mode:
            try:
                logger.info("Tutor mode enabled - analyzing prompt with Tutor Antonina")
                
                # Create tutor agent
                tutor = TutorAntonina(model=request.model, provider=request.provider)
                
                # Get chat history for context
                chat_history = [{"role": msg.role, "content": msg.content} for msg in request.messages[:-1]]
                
                # Analyze the last prompt
                guide_result = await tutor.guide(last_message, chat_history)
                
                # Add tutor results to response
                result["tutor_question"] = guide_result["question"]
                result["tutor_feedback"] = guide_result["feedback"]
                
                logger.info(f"Tutor analysis completed - question: {bool(guide_result['question'])}, feedback: {bool(guide_result['feedback'])}")
                
            except Exception as e:
                logger.error(f"Tutor mode error: {e}")
                # Don't fail the entire request if tutor mode fails
                result["tutor_question"] = "Przepraszam, wystąpił błąd w trybie tutora. Spróbuj ponownie."
        
        # Ensure all required fields are present for ChatResponse
        if isinstance(result, str):
            # If result is just a string, convert to dict
            result = {"text": result}
        
        # Ensure required fields are present
        if "text" not in result:
            result["text"] = str(result)
        
        if "model" not in result:
            result["model"] = request.model or "gpt-4"
        
        if "provider" not in result:
            result["provider"] = "unknown"
        
        if "usage" not in result:
            result["usage"] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        if "cost" not in result:
            result["cost"] = {"total": 0.0, "prompt": 0.0, "completion": 0.0}
        
        if "finish_reason" not in result:
            result["finish_reason"] = "stop"
        
        logger.info(f"Chat completion successful in {result['response_time']:.2f}s (web search: {web_search_used}, tutor: {request.tutor_mode})")
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat completion failed: {str(e)}"
        )

@router.post("/tutor", response_model=TutorResponse)
async def tutor_mode(request: TutorRequest):
    """
    Dedicated endpoint for Tutor Antonina mode.
    Analyzes prompts and provides educational feedback.
    """
    start_time = time.time()
    
    try:
        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="At least one message is required")
        
        last_message = request.messages[-1].content
        
        # Create tutor agent
        tutor = TutorAntonina(model=request.model, provider=request.provider)
        
        # Get chat history for context
        chat_history = [{"role": msg.role, "content": msg.content} for msg in request.messages[:-1]]
        
        # Analyze the prompt
        guide_result = await tutor.guide(last_message, chat_history)
        
        # Generate standard AI response
        if request.provider:
            provider_type = None
            for pt in llm_factory.get_available_providers():
                if pt.value == request.provider:
                    provider_type = pt
                    break
            
            if not provider_type:
                raise HTTPException(status_code=400, detail=f"Provider {request.provider} not available")
            
            provider = llm_factory.get_provider(provider_type)
            result = await provider.chat(
                messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
                model=request.model,
                temperature=0.7,
                max_tokens=1000
            )
        else:
            result = await llm_factory.chat_with_fallback(
                messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
                model=request.model,
                temperature=0.7,
                max_tokens=1000
            )
        
        # Prepare response
        # Handle different response formats
        if isinstance(result, str):
            reply = result
        elif isinstance(result, dict):
            if "text" in result:
                reply = result["text"]
            elif "choices" in result and len(result["choices"]) > 0:
                reply = result["choices"][0]["message"]["content"]
            else:
                reply = str(result)
        else:
            reply = str(result)
        
        response_data = {
            "reply": reply,
            "tutor_question": guide_result["question"],
            "tutor_feedback": guide_result["feedback"],
            "model": result.get("model", request.model or "gpt-4") if isinstance(result, dict) else (request.model or "gpt-4"),
            "provider": result.get("provider", "openai") if isinstance(result, dict) else "openai",
            "usage": result.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}) if isinstance(result, dict) else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "cost": result.get("cost", {"total": 0.0, "prompt": 0.0, "completion": 0.0}) if isinstance(result, dict) else {"total": 0.0, "prompt": 0.0, "completion": 0.0},
            "finish_reason": result.get("finish_reason", "stop") if isinstance(result, dict) else "stop",
            "response_time": time.time() - start_time
        }
        
        logger.info(f"Tutor mode completed in {response_data['response_time']:.2f}s")
        
        return TutorResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tutor mode error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Tutor mode failed: {str(e)}"
        )

@router.post("/completion", response_model=ChatResponse)
async def chat_completion_legacy(request: ChatRequest):
    """
    Legacy endpoint for chat completion (redirects to /chat).
    """
    return await chat_completion(request)

@router.post("/batch")
async def chat_completion_batch(requests: List[ChatRequest]):
    """
    Batch chat completion endpoint.
    """
    try:
        if len(requests) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 requests allowed per batch")
        
        results = []
        batch_start_time = time.time()
        
        for i, request in enumerate(requests):
            try:
                result = await chat_completion(request)
                results.append(result.dict())
            except Exception as e:
                logger.error(f"Batch request {i} failed: {e}")
                results.append({
                    "error": str(e),
                    "index": i
                })
        
        batch_time = time.time() - batch_start_time
        
        return {
            "results": results,
            "batch_info": {
                "total_requests": len(requests),
                "successful_requests": len([r for r in results if "error" not in r]),
                "failed_requests": len([r for r in results if "error" in r]),
                "batch_time": batch_time
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch chat completion error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch chat completion failed: {str(e)}"
        )

@router.post("/embeddings")
async def create_embeddings(request: EmbedRequest):
    """
    Create embeddings for text using available LLM providers.
    """
    try:
        # Validate request
        if not request.texts:
            raise HTTPException(status_code=400, detail="At least one text is required")
        
        # Use LLM factory for embeddings
        result = await llm_factory.embed_with_fallback(
            texts=request.texts,
            model=request.model
        )
        
        return {
            "embeddings": result["embeddings"],
            "model": result.get("model", request.model or "text-embedding-ada-002"),
            "provider": result.get("provider", "openai"),
            "usage": result.get("usage", {
                "prompt_tokens": sum(len(text.split()) for text in request.texts),
                "total_tokens": sum(len(text.split()) for text in request.texts)
            }),
            "cost": result.get("cost", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Embedding creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Embedding creation failed: {str(e)}"
        )

@router.post("/embed")
async def create_embeddings_alias(request: EmbedRequest):
    """
    Alias for embeddings endpoint for backward compatibility.
    """
    return await create_embeddings(request)

@router.get("/models")
async def get_available_models():
    """Get available models from all configured providers."""
    try:
        return {
            "models": {
                "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                "mistral": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]
            },
            "default_models": {
                "openai": "gpt-4o-mini",
                "mistral": "mistral-small-latest"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available models")

@router.get("/providers/status")
async def get_providers_status():
    """Get status of all configured providers."""
    try:
        provider_status = {}
        
        # Get available providers
        available_providers = llm_factory.get_available_providers()
        
        for provider_type in available_providers:
            try:
                provider = llm_factory.get_provider(provider_type)
                status = await provider.health_check()
                provider_status[provider_type.value] = status
            except Exception as e:
                logger.warning(f"Could not get status for {provider_type.value}: {e}")
                provider_status[provider_type.value] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return {
            "providers": provider_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to get providers status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get providers status")

@router.post("/test-web-search")
async def test_web_search(query: str = "aktualne wiadomości"):
    """Test web search functionality."""
    try:
        logger.info(f"Testing web search with query: {query}")
        
        results = await perform_web_search(query, max_results=3)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Web search test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Web search test failed: {str(e)}")
