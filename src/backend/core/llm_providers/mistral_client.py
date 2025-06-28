"""
Mistral AI LLM Provider.
Zapewnia integrację z Mistral AI API dla LLM operations.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from backend.config import settings
from .provider_factory import BaseLLMProvider

logger = logging.getLogger(__name__)


class MistralConfig(BaseModel):
    """Configuration for Mistral provider"""
    
    model_name: str
    max_tokens: int
    temperature: float
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_streaming: bool = True
    supports_vision: bool = True


class MistralProvider(BaseLLMProvider):
    """
    Mistral AI LLM Provider.
    Zapewnia integrację z Mistral AI API dla LLM operations.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize Mistral provider"""
        super().__init__(api_key)
        
        self.base_url = settings.MISTRAL_BASE_URL
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": settings.USER_AGENT,
            }
        )
        
        # Model configurations for Mistral
        self.models = {
            "mistral-large-latest": MistralConfig(
                model_name="mistral-large-latest",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.007,
                cost_per_1k_output=0.024,
                supports_streaming=True,
                supports_vision=True,
            ),
            "mistral-medium-latest": MistralConfig(
                model_name="mistral-medium-latest",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0024,
                cost_per_1k_output=0.0072,
                supports_streaming=True,
                supports_vision=True,
            ),
            "mistral-small-latest": MistralConfig(
                model_name="mistral-small-latest",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0007,
                cost_per_1k_output=0.0024,
                supports_streaming=True,
                supports_vision=True,
            ),
        }
        
        # Default model
        self.default_model = settings.MISTRAL_CHAT_MODEL
        
        logger.info(f"Mistral provider initialized with model: {self.default_model}")

    async def chat(
        self, 
        messages: List[Dict[str, Any]], 
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """
        Generate chat completion using Mistral AI.
        
        Args:
            messages: List of message dictionaries
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            model_name = model or self.default_model
            model_config = self.models.get(model_name)
            
            if not model_config:
                logger.warning(f"Model {model_name} not found, using default")
                model_name = self.default_model
                model_config = self.models.get(model_name)
            
            # Prepare request payload
            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", model_config.max_tokens if model_config else 4096),
                "temperature": kwargs.get("temperature", model_config.temperature if model_config else 0.1),
                "stream": kwargs.get("stream", False),
            }
            
            # Add optional parameters
            if "top_p" in kwargs:
                payload["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                payload["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                payload["presence_penalty"] = kwargs["presence_penalty"]
            
            logger.debug(f"Mistral chat request: model={model_name}, messages_count={len(messages)}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Mistral API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract response text
            response_text = response_data["choices"][0]["message"]["content"]
            
            # Calculate usage and cost
            usage = response_data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            cost = self.calculate_cost(model_name, input_tokens, output_tokens)
            
            logger.info(
                f"Mistral chat completed: model={model_name}, tokens={total_tokens}, cost=${cost:.4f}"
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Mistral chat error: {e}")
            raise Exception(f"Mistral chat failed: {e}")

    async def embed(self, text: str, model: Optional[str] = None, **kwargs: Any) -> List[float]:
        """
        Generate embeddings using Mistral AI.
        
        Args:
            text: Text to embed
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Mistral uses a separate embedding model
            embedding_model = "mistral-embed"
            
            # Prepare request payload
            payload = {
                "model": embedding_model,
                "input": text,
            }
            
            logger.debug(f"Mistral embed request: model={embedding_model}, text_length={len(text)}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/embeddings",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Mistral API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract embedding
            embedding = response_data["data"][0]["embedding"]
            
            # Calculate usage
            usage = response_data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            
            logger.info(f"Mistral embed completed: model={embedding_model}, tokens={total_tokens}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Mistral embed error: {e}")
            raise Exception(f"Mistral embed failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check if Mistral API is available"""
        try:
            # Try to list models to check API connectivity
            response = await self.http_client.get(f"{self.base_url}/models")
            
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model["id"] for model in models_data.get("data", [])]
                
                return {
                    "status": "healthy",
                    "models_count": len(available_models),
                    "available_models": available_models,
                    "provider": "mistral",
                    "default_model": self.default_model,
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"API returned status {response.status_code}",
                    "provider": "mistral",
                }
                
        except Exception as e:
            logger.error(f"Mistral health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "mistral",
            }

    def get_model_info(self, model_name: str) -> Optional[MistralConfig]:
        """Get information about a specific model"""
        return self.models.get(model_name)

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())

    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage"""
        model_config = self.models.get(model_name)
        if not model_config:
            return 0.0
        
        input_cost = (input_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model_config.cost_per_1k_output
        return input_cost + output_cost

    async def close(self) -> None:
        """Close HTTP client"""
        await self.http_client.aclose() 