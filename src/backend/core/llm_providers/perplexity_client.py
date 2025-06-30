"""
Perplexity API client for Ageny Online.
Implementacja klienta Perplexity API zgodnie z dokumentacją.
"""

import logging
import time
from typing import Dict, List, Any, Optional
import httpx
from pydantic import BaseModel

from backend.config import settings

logger = logging.getLogger(__name__)


class PerplexityConfig(BaseModel):
    """Configuration for Perplexity models."""
    model_name: str
    max_tokens: int
    temperature: float
    cost_per_1k: float
    supports_streaming: bool
    supports_search: bool


class PerplexityProvider:
    """Perplexity API provider implementation."""
    
    def __init__(self, api_key: str = None):
        """Initialize Perplexity provider."""
        self.api_key = api_key or settings.perplexity_api_key
        self.base_url = settings.PERPLEXITY_BASE_URL
        
        # Configure models
        self.models = {
            "sonar-pro": PerplexityConfig(
                model_name="sonar-pro",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k=0.0002,  # $0.20 per 1M tokens
                supports_streaming=True,
                supports_search=True
            ),
            "sonar-pro-online": PerplexityConfig(
                model_name="sonar-pro-online",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k=0.0002,
                supports_streaming=True,
                supports_search=True
            ),
            "sonar-small-online": PerplexityConfig(
                model_name="sonar-small-online",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k=0.0001,  # $0.10 per 1M tokens
                supports_streaming=True,
                supports_search=True
            ),
            "llama-3.1-8b-online": PerplexityConfig(
                model_name="llama-3.1-8b-online",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k=0.00005,  # $0.05 per 1M tokens
                supports_streaming=True,
                supports_search=True
            )
        }
        
        self.default_model = settings.PERPLEXITY_CHAT_MODEL
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": settings.USER_AGENT
            }
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Perplexity API.
        
        Args:
            messages: List of message dictionaries
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with completion data
        """
        try:
            model_name = model or self.default_model
            model_config = self.models.get(model_name)
            
            if not model_config:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Prepare request payload
            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": max_tokens or model_config.max_tokens,
                "temperature": temperature or model_config.temperature,
                **kwargs
            }
            
            logger.debug(f"Perplexity chat request: model={model_name}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Perplexity API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract completion data
            choices = response_data.get("choices", [])
            if not choices:
                raise Exception("No choices in Perplexity response")
            
            choice = choices[0]
            content = choice.get("message", {}).get("content", "")
            
            # Calculate usage and cost
            usage = response_data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            cost = self.calculate_cost(model_name, tokens_used)
            
            return {
                "text": content,
                "model": model_name,
                "provider": "perplexity",
                "usage": usage,
                "cost": cost,
                "finish_reason": choice.get("finish_reason", "stop"),
                "metadata": {
                    "provider": "perplexity",
                    "model": model_name,
                    "tokens_used": tokens_used,
                    "response_time": time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Perplexity chat error: {e}")
            raise Exception(f"Perplexity chat failed: {e}")
    
    async def search(
        self,
        query: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send search request to Perplexity API.
        
        Args:
            query: Search query
            model: Model to use (defaults to search model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with search results
        """
        try:
            model_name = model or settings.PERPLEXITY_SEARCH_MODEL
            model_config = self.models.get(model_name)
            
            if not model_config:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Prepare messages for search
            messages = [
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            # Add search parameters
            search_kwargs = {
                "search_domain_filter": kwargs.get("search_domain_filter"),
                "date_range_filter": kwargs.get("date_range_filter"),
                "academic_filter": kwargs.get("academic_filter"),
                "image_filter": kwargs.get("image_filter"),
                "user_location_filter": kwargs.get("user_location_filter"),
                **kwargs
            }
            
            # Remove None values
            search_kwargs = {k: v for k, v in search_kwargs.items() if v is not None}
            
            # Make chat request with search capabilities
            return await self.chat(
                messages=messages,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                **search_kwargs
            )
            
        except Exception as e:
            logger.error(f"Perplexity search error: {e}")
            raise Exception(f"Perplexity search failed: {e}")
    
    def calculate_cost(self, model_name: str, tokens_used: int) -> float:
        """Calculate cost for tokens used."""
        model_config = self.models.get(model_name)
        if not model_config:
            return 0.0
        
        return (tokens_used / 1000) * model_config.cost_per_1k
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Perplexity API health."""
        try:
            # Make a simple request to check API health
            response = await self.http_client.get(f"{self.base_url}/models")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "provider": "perplexity",
                    "models_available": len(response.json().get("data", [])),
                    "timestamp": time.time()
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": "perplexity",
                    "error": f"HTTP {response.status_code}",
                    "timestamp": time.time()
                }
                
        except Exception as e:
            logger.error(f"Perplexity health check failed: {e}")
            return {
                "status": "unhealthy",
                "provider": "perplexity",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
        except:
            pass
