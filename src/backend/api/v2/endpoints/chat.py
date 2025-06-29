<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
=======
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
<<<<<<< HEAD
import re

from backend.core.llm_providers.provider_factory import provider_factory
from backend.api.v2.endpoints.web_search import WebSearchRequest, search_providers
=======
import asyncio

from ....config import get_settings
from ....core.llm_providers.provider_factory import llm_factory, ProviderType, ProviderConfig
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8

logger = logging.getLogger(__name__)

router = APIRouter()

<<<<<<< HEAD
=======
settings = get_settings()

>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
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
<<<<<<< HEAD
    enable_web_search: bool = Field(True, description="Whether to enable web search for current information")
=======
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8

class ChatResponse(BaseModel):
    """Chat completion response model."""
    text: str
    model: str
    provider: str
    usage: Dict[str, int]
    cost: Dict[str, float]
    finish_reason: str
    response_time: float
<<<<<<< HEAD
    web_search_used: bool = False
    web_search_results: Optional[List[Dict[str, Any]]] = None

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

@router.post("/completion", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate chat completion using available LLM providers with optional web search.
=======

class EmbedRequest(BaseModel):
    """Embedding request model."""
    texts: List[str] = Field(..., description="List of texts to embed")
    model: Optional[str] = Field(None, description="Model to use for embedding")

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate chat completion using available LLM providers.
    
    This endpoint automatically selects the best available provider based on configuration
    and falls back to alternatives if the primary provider fails.
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
    """
    start_time = time.time()
    
    try:
<<<<<<< HEAD
        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="At least one message is required")
        
        last_message = request.messages[-1].content
        web_search_used = False
        web_search_results = None
        
        # Check if web search should be used
        if request.enable_web_search and should_use_web_search(last_message):
            logger.info(f"Performing web search for query: {last_message}")
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
        
        # Generate response using LLM provider
        # For now, using mock response - in real implementation, use provider_factory
        result = {
            "text": f"Odpowiedź na: {last_message}" + (" (z aktualnymi informacjami z internetu)" if web_search_used else ""),
            "model": request.model or "gpt-4o-mini",
            "provider": request.provider or "openai",
            "usage": {
                "prompt_tokens": len(last_message.split()),
                "completion_tokens": 10,
                "total_tokens": len(last_message.split()) + 10
            },
            "cost": {
                "input_cost": 0.001,
                "output_cost": 0.002,
                "total_cost": 0.003
            },
            "finish_reason": "stop",
            "response_time": time.time() - start_time,
            "web_search_used": web_search_used,
            "web_search_results": web_search_results
        }
        
        logger.info(f"Chat completion successful in {result['response_time']:.2f}s (web search: {web_search_used})")
=======
        # Convert messages to the format expected by providers
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Validate messages
        if not messages:
            raise HTTPException(status_code=400, detail="At least one message is required")
        
        # Check if specific provider is requested
        if request.provider:
            try:
                provider_type = ProviderType(request.provider)
                provider = llm_factory.get_provider(provider_type)
                
                # Adapt model name for provider if needed
                adapted_model = llm_factory._adapt_model_for_provider(request.model, provider_type)
                
                result = await provider.chat(
                    messages=messages,
                    model=adapted_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )
                result["provider"] = request.provider
                
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
            except Exception as e:
                logger.error(f"Provider {request.provider} failed: {e}")
                raise HTTPException(status_code=500, detail=f"Provider {request.provider} failed")
        else:
            # Use fallback mechanism
            result = await llm_factory.chat_with_fallback(
                messages=messages,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Add response time to result
        result["response_time"] = response_time
        
        logger.info(f"Chat completion successful with {result['provider']} in {response_time:.2f}s")
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail="Chat completion failed")

<<<<<<< HEAD
=======
@router.post("/batch")
async def chat_completion_batch(requests: List[ChatRequest]):
    """
    Generate chat completions for multiple requests in batch.
    
    This endpoint processes multiple chat requests concurrently for better performance.
    """
    start_time = time.time()
    
    try:
        # Process requests concurrently
        tasks = []
        for req in requests:
            messages = [{"role": msg.role, "content": msg.content} for msg in req.messages]
            task = llm_factory.chat_with_fallback(
                messages=messages,
                model=req.model,
                max_tokens=req.max_tokens,
                temperature=req.temperature
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Request {i} failed: {result}")
                processed_results.append({
                    "text": "",
                    "model": "",
                    "provider": "",
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    "cost": {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0},
                    "finish_reason": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        # Calculate total cost and usage
        total_cost = sum(r.get("cost", {}).get("total_cost", 0) for r in processed_results)
        total_tokens = sum(r.get("usage", {}).get("total_tokens", 0) for r in processed_results)
        
        response_time = time.time() - start_time
        
        return {
            "results": processed_results,
            "batch_info": {
                "total_requests": len(requests),
                "successful_requests": len([r for r in processed_results if "error" not in r]),
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "response_time": response_time
            }
        }
        
    except Exception as e:
        logger.error(f"Batch chat completion failed: {e}")
        raise HTTPException(status_code=500, detail="Batch chat completion failed")

>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
@router.get("/models")
async def get_available_models():
    """Get available models from all configured providers."""
    try:
<<<<<<< HEAD
        return {
            "models": {
                "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                "mistral": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]
            },
=======
        models = {}
        
        for provider_type in ProviderType:
            try:
                provider = llm_factory.get_provider(provider_type)
                models[provider_type.value] = provider.get_available_models()
            except Exception as e:
                logger.warning(f"Could not get models for {provider_type.value}: {e}")
                models[provider_type.value] = []
        
        return {
            "models": models,
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
            "default_models": {
                "openai": "gpt-4o-mini",
                "mistral": "mistral-small-latest"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")

@router.get("/providers/status")
<<<<<<< HEAD
async def get_providers_status():
    """Get status of all configured providers."""
    try:
        provider_status = {}
        
        # Get available providers
        available_providers = provider_factory.get_available_providers()
        
        for provider_type in available_providers:
            try:
                provider = provider_factory.get_provider(provider_type)
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
=======
async def get_provider_status():
    """Get status of all LLM providers."""
    try:
        return {
            "providers": llm_factory.get_provider_status(),
            "available_providers": llm_factory.get_available_providers(),
            "fallback_order": llm_factory._fallback_order
        }
        
    except Exception as e:
        logger.error(f"Failed to get provider status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get provider status")

@router.post("/embed")
async def create_embeddings(request: EmbedRequest):
    """
    Create embeddings for text using available providers.
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="At least one text is required")
        
        result = await llm_factory.embed_with_fallback(
            texts=request.texts,
            model=request.model
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Embedding creation failed: {e}")
        raise HTTPException(status_code=500, detail="Embedding creation failed") 
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
