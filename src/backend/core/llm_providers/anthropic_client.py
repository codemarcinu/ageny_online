"""
Anthropic LLM Provider.
Zapewnia integrację z Anthropic API dla LLM operations.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from backend.config import settings
from .provider_factory import BaseLLMProvider

logger = logging.getLogger(__name__)


class AnthropicConfig(BaseModel):
    """Configuration for Anthropic provider"""
    
    model_name: str
    max_tokens: int
    temperature: float
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_streaming: bool = True
    supports_vision: bool = True


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic LLM Provider.
    Zapewnia integrację z Anthropic API dla LLM operations.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize Anthropic provider"""
        super().__init__(api_key)
        
        self.base_url = "https://api.anthropic.com"
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": settings.USER_AGENT,
            }
        )
        
        # Model configurations for Anthropic
        self.models = {
            "claude-3-opus-20240229": AnthropicConfig(
                model_name="claude-3-opus-20240229",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.015,
                cost_per_1k_output=0.075,
                supports_streaming=True,
                supports_vision=True,
            ),
            "claude-3-sonnet-20240229": AnthropicConfig(
                model_name="claude-3-sonnet-20240229",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                supports_streaming=True,
                supports_vision=True,
            ),
            "claude-3-haiku-20240307": AnthropicConfig(
                model_name="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                supports_streaming=True,
                supports_vision=True,
            ),
        }
        
        # Default model
        self.default_model = "claude-3-sonnet-20240229"
        
        logger.info(f"Anthropic provider initialized with model: {self.default_model}")

    async def chat(
        self, 
        messages: List[Dict[str, Any]], 
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """
        Generate chat completion using Anthropic.
        
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
            
            # Convert messages to Anthropic format
            anthropic_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    anthropic_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    anthropic_messages.append({"role": "assistant", "content": msg["content"]})
                elif msg["role"] == "system":
                    # Anthropic doesn't support system messages in the same way
                    # We'll prepend it to the first user message
                    if anthropic_messages and anthropic_messages[0]["role"] == "user":
                        anthropic_messages[0]["content"] = f"{msg['content']}\n\n{anthropic_messages[0]['content']}"
            
            # Prepare request payload
            payload = {
                "model": model_name,
                "messages": anthropic_messages,
                "max_tokens": kwargs.get("max_tokens", model_config.max_tokens if model_config else 4096),
                "temperature": kwargs.get("temperature", model_config.temperature if model_config else 0.1),
            }
            
            logger.debug(f"Anthropic chat request: model={model_name}, messages_count={len(anthropic_messages)}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/v1/messages",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract response text
            response_text = response_data["content"][0]["text"]
            
            # Calculate usage and cost
            usage = response_data.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            
            cost = self.calculate_cost(model_name, input_tokens, output_tokens)
            
            logger.info(
                f"Anthropic chat completed: model={model_name}, tokens={input_tokens + output_tokens}, cost=${cost:.4f}"
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise Exception(f"Anthropic chat failed: {e}")

    async def embed(self, text: str, model: Optional[str] = None, **kwargs: Any) -> List[float]:
        """
        Generate embeddings using Anthropic.
        
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
            # Anthropic uses a separate embedding model
            embedding_model = "claude-3-sonnet-20240229"
            
            # Prepare request payload
            payload = {
                "model": embedding_model,
                "input": text,
            }
            
            logger.debug(f"Anthropic embed request: model={embedding_model}, text_length={len(text)}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/v1/embeddings",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Anthropic embedding API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract embedding
            embedding = response_data["data"][0]["embedding"]
            
            logger.debug(f"Anthropic embed completed: model={embedding_model}, embedding_length={len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Anthropic embed error: {e}")
            raise Exception(f"Anthropic embed failed: {e}")

    async def complete_text(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> str:
        """
        Complete text using Anthropic (alias for chat with single message).
        
        Args:
            prompt: Text prompt to complete
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            Completed text
            
        Raises:
            Exception: If API call fails
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, model, **kwargs)

    async def embed_text(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embeddings for text (alias for embed method).
        
        Args:
            text: Text to embed
            model: Embedding model to use (defaults to configured model)
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: If API call fails
        """
        return await self.embed(text, model)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of Anthropic API.
        
        Returns:
            Health status dictionary
        """
        try:
            # Simple health check - try to get model info
            response = await self.http_client.get(f"{self.base_url}/v1/models")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "provider": "anthropic",
                    "models_available": True
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": "anthropic",
                    "error": f"API returned {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "anthropic",
                "error": str(e)
            }

    def get_model_info(self, model_name: str) -> Optional[AnthropicConfig]:
        """Get configuration for a specific model"""
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