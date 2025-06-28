from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
import re

from backend.core.llm_providers.provider_factory import provider_factory
from backend.api.v2.endpoints.web_search import WebSearchRequest, search_providers

logger = logging.getLogger(__name__)

router = APIRouter()

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
    """
    start_time = time.time()
    
    try:
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
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail="Chat completion failed")

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
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")

@router.get("/providers/status")
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