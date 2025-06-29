"""
Cohere LLM Provider.
Zapewnia integrację z Cohere API dla LLM operations.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from backend.config import settings
from .provider_factory import BaseLLMProvider

logger = logging.getLogger(__name__)


class CohereConfig(BaseModel):
    """Configuration for Cohere provider"""
    
    model_name: str
    max_tokens: int
    temperature: float
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_streaming: bool = True
    supports_vision: bool = False


class CohereProvider(BaseLLMProvider):
    """
    Cohere LLM Provider.
    Zapewnia integrację z Cohere API dla LLM operations.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize Cohere provider"""
        super().__init__(api_key)
        
        self.base_url = "https://api.cohere.ai"
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": settings.USER_AGENT,
            }
        )
        
        # Model configurations for Cohere
        self.models = {
            "command": CohereConfig(
                model_name="command",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0015,
                cost_per_1k_output=0.002,
                supports_streaming=True,
                supports_vision=False,
            ),
            "command-light": CohereConfig(
                model_name="command-light",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0003,
                cost_per_1k_output=0.0006,
                supports_streaming=True,
                supports_vision=False,
            ),
            "command-nightly": CohereConfig(
                model_name="command-nightly",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0015,
                cost_per_1k_output=0.002,
                supports_streaming=True,
                supports_vision=False,
            ),
        }
        
        # Default model
        self.default_model = "command"
        
        logger.info(f"Cohere provider initialized with model: {self.default_model}")

    async def chat(
        self, 
        messages: List[Dict[str, Any]], 
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """
        Generate chat completion using Cohere.
        
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
            
            # Convert messages to Cohere format
            # Cohere uses a different format - we'll combine all messages into a single prompt
            prompt = ""
            for msg in messages:
                if msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
                elif msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
            
            prompt += "Assistant:"
            
            # Prepare request payload
            payload = {
                "model": model_name,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", model_config.max_tokens if model_config else 4096),
                "temperature": kwargs.get("temperature", model_config.temperature if model_config else 0.1),
                "stream": kwargs.get("stream", False),
            }
            
            # Add optional parameters
            if "top_p" in kwargs:
                payload["p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                payload["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                payload["presence_penalty"] = kwargs["presence_penalty"]
            
            logger.debug(f"Cohere chat request: model={model_name}, prompt_length={len(prompt)}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/v1/generate",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Cohere API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract response text
            response_text = response_data["generations"][0]["text"]
            
            # Calculate usage and cost
            usage = response_data.get("meta", {}).get("billed_units", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            
            cost = self.calculate_cost(model_name, input_tokens, output_tokens)
            
            logger.info(
                f"Cohere chat completed: model={model_name}, tokens={input_tokens + output_tokens}, cost=${cost:.4f}"
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Cohere chat error: {e}")
            raise Exception(f"Cohere chat failed: {e}")

    async def embed(self, text: str, model: Optional[str] = None, **kwargs: Any) -> List[float]:
        """
        Generate embeddings using Cohere.
        
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
            # Cohere uses a separate embedding model
            embedding_model = "embed-english-v3.0"
            
            # Prepare request payload
            payload = {
                "texts": [text],
                "model": embedding_model,
            }
            
            logger.debug(f"Cohere embed request: model={embedding_model}, text_length={len(text)}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/v1/embed",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Cohere embedding API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract embedding
            embedding = response_data["embeddings"][0]
            
            logger.debug(f"Cohere embed completed: model={embedding_model}, embedding_length={len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Cohere embed error: {e}")
            raise Exception(f"Cohere embed failed: {e}")

    async def complete_text(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> str:
        """
        Complete text using Cohere (alias for chat with single message).
        
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
        Check health of Cohere API.
        
        Returns:
            Health status dictionary
        """
        try:
            # Simple health check - try to get model info
            response = await self.http_client.get(f"{self.base_url}/v1/models")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "provider": "cohere",
                    "models_available": True
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": "cohere",
                    "error": f"API returned {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "cohere",
                "error": str(e)
            }

    def get_model_info(self, model_name: str) -> Optional[CohereConfig]:
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