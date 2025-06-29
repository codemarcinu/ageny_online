<<<<<<< HEAD
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
=======
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import httpx
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a specific Mistral model."""
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    context_length: int

class MistralProvider:
    """Mistral AI API provider for chat completions and embeddings."""
    
    def __init__(self, api_key: str):
        """
        Initialize Mistral provider.
        
        Args:
            api_key: Mistral API key
        """
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        self.client = MistralClient(api_key=api_key)
        
        # Model configurations with costs (as of 2024)
        self.models = {
            "mistral-large-latest": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.007,
                cost_per_1k_output=0.024,
                context_length=32768
            ),
            "mistral-medium-latest": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.0027,
                cost_per_1k_output=0.0081,
                context_length=32768
            ),
            "mistral-small-latest": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00042,
                context_length=32768
            ),
            "open-mistral-7b": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00042,
                context_length=32768
            )
        }
        
        self.default_model = "mistral-small-latest"
        logger.info(f"Mistral provider initialized with default model: {self.default_model}")
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters for Mistral API
            
        Returns:
            Dictionary containing response text, usage, and cost
        """
        model = model or self.default_model
        
        if model not in self.models:
            raise ValueError(f"Unsupported model: {model}")
        
        model_config = self.models[model]
        max_tokens = max_tokens or model_config.max_tokens
        
        try:
            logger.debug(f"Generating chat completion with model: {model}")
            
            # Convert messages to Mistral format
            mistral_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]
            
            response = await asyncio.to_thread(
                self.client.chat,
                model=model,
                messages=mistral_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Calculate costs
            usage = response.usage
            input_cost = (usage.prompt_tokens / 1000) * model_config.cost_per_1k_input
            output_cost = (usage.completion_tokens / 1000) * model_config.cost_per_1k_output
            total_cost = input_cost + output_cost
            
            result = {
                "text": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "cost": {
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": total_cost
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"Chat completion successful. Cost: ${total_cost:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Mistral chat completion: {e}")
            raise
    
    async def embed(
        self, 
        texts: Union[str, List[str]], 
        model: str = "mistral-embed"
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of text strings
            model: Embedding model to use
            
        Returns:
            Dictionary containing embeddings and usage info
        """
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            
            response = await asyncio.to_thread(
                self.client.embeddings,
                model=model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            usage = response.usage
            
            # Calculate cost (mistral-embed: $0.0001 per 1M tokens)
            cost_per_1m = 0.0001
            total_cost = (usage.total_tokens / 1_000_000) * cost_per_1m
            
            result = {
                "embeddings": embeddings,
                "model": model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "total_tokens": usage.total_tokens
                },
                "cost": total_cost
            }
            
            logger.info(f"Embeddings generated successfully. Cost: ${total_cost:.6f}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())
    
    def get_model_config(self, model: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        return self.models.get(model) 
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
