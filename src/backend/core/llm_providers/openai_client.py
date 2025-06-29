<<<<<<< HEAD
"""
OpenAI Provider for LLM operations.
Zapewnia integrację z OpenAI API dla chat i embedding operations.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import openai
from pydantic import BaseModel

from backend.config import settings

logger = logging.getLogger(__name__)


class OpenAIProviderConfig(BaseModel):
    """Configuration for OpenAI provider"""
    
    model_name: str
    max_tokens: int
    temperature: float
    cost_per_1k: float
    supports_streaming: bool = True
    supports_embedding: bool = False


class OpenAIProvider:
    """
    OpenAI Provider for LLM operations.
    Zapewnia integrację z OpenAI API dla chat i embedding operations.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize OpenAI provider"""
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            organization=settings.OPENAI_ORGANIZATION,
            base_url=settings.OPENAI_BASE_URL,
        )
        
        # Model configurations
        self.models = {
            "gpt-4": OpenAIProviderConfig(
                model_name="gpt-4",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k=0.03,
                supports_streaming=True,
                supports_embedding=False,
            ),
            "gpt-4-turbo": OpenAIProviderConfig(
                model_name="gpt-4-turbo-preview",
                max_tokens=128000,
                temperature=0.7,
                cost_per_1k=0.01,
                supports_streaming=True,
                supports_embedding=False,
            ),
            "gpt-3.5-turbo": OpenAIProviderConfig(
                model_name="gpt-3.5-turbo",
                max_tokens=16385,
                temperature=0.7,
                cost_per_1k=0.002,
                supports_streaming=True,
                supports_embedding=False,
            ),
        }
        
        # Default model
        self.default_chat_model = settings.OPENAI_CHAT_MODEL
        self.default_embedding_model = settings.OPENAI_EMBEDDING_MODEL
        
        logger.info(f"OpenAI provider initialized with model: {self.default_chat_model}")

=======
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    context_length: int

class OpenAIProvider:
    """OpenAI API provider for chat completions and embeddings."""
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            organization: OpenAI organization ID (optional)
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=organization
        )
        
        # Model configurations with costs (as of 2024)
        self.models = {
            "gpt-4o": ModelConfig(
                max_tokens=128000,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.015,
                context_length=128000
            ),
            "gpt-4o-mini": ModelConfig(
                max_tokens=128000,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                context_length=128000
            ),
            "gpt-4-turbo": ModelConfig(
                max_tokens=128000,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                context_length=128000
            ),
            "gpt-3.5-turbo": ModelConfig(
                max_tokens=16385,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                context_length=16385
            )
        }
        
        self.default_model = "gpt-4o-mini"
        logger.info(f"OpenAI provider initialized with default model: {self.default_model}")
    
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
<<<<<<< HEAD
        temperature: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> str:
        """
        Generate chat completion using OpenAI API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to configured model)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            stream: Whether to stream the response
            **kwargs: Additional parameters for OpenAI API
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails
        """
        try:
            model_name = model or self.default_chat_model
            model_config = self.models.get(model_name)
            
            if not model_config:
                logger.warning(f"Model {model_name} not found, using default")
                model_name = self.default_chat_model
                model_config = self.models.get(model_name)
            
            # Use configured defaults if not provided
            max_tokens = max_tokens or model_config.max_tokens if model_config else settings.OPENAI_MAX_TOKENS
            temperature = temperature or model_config.temperature if model_config else settings.OPENAI_TEMPERATURE
            
            logger.debug(f"OpenAI chat request: model={model_name}, max_tokens={max_tokens}, temperature={temperature}")
            
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                **kwargs
            )
            
            if stream:
                return response  # Return streaming response object
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise Exception(f"OpenAI chat failed: {e}")

    async def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embeddings using OpenAI API.
        
        Args:
            text: Text to embed
            model: Embedding model to use (defaults to configured model)
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: If API call fails
        """
        try:
            model_name = model or self.default_embedding_model
            
            logger.debug(f"OpenAI embed request: model={model_name}, text_length={len(text)}")
            
            response = await self.client.embeddings.create(
                model=model_name,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI embed error: {e}")
            raise Exception(f"OpenAI embed failed: {e}")

    async def embed_batch(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using OpenAI API.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use (defaults to configured model)
            
        Returns:
            List of embedding lists
            
        Raises:
            Exception: If API call fails
        """
        try:
            model_name = model or self.default_embedding_model
            
            logger.debug(f"OpenAI embed batch request: model={model_name}, texts_count={len(texts)}")
            
            response = await self.client.embeddings.create(
                model=model_name,
                input=texts
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"OpenAI embed batch error: {e}")
            raise Exception(f"OpenAI embed batch failed: {e}")

    def get_model_info(self, model_name: str) -> Optional[OpenAIProviderConfig]:
        """Get information about a specific model"""
        return self.models.get(model_name)

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())

    def calculate_cost(self, model_name: str, tokens: int) -> float:
        """Calculate cost for token usage"""
        model_config = self.models.get(model_name)
        if not model_config:
            return 0.0
        return (tokens / 1000) * model_config.cost_per_1k

    async def health_check(self) -> Dict[str, Any]:
        """Check if OpenAI API is available"""
        try:
            # Try to list models to check API connectivity
            models = await self.client.models.list()
            return {
                "status": "healthy",
                "models_count": len(models.data),
                "provider": "openai",
                "default_chat_model": self.default_chat_model,
                "default_embedding_model": self.default_embedding_model,
            }
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "openai",
            } 
=======
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
            **kwargs: Additional parameters for OpenAI API
            
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
            
            response: ChatCompletion = await self.client.chat.completions.create(
                model=model,
                messages=messages,
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
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            raise
    
    async def embed(
        self, 
        texts: Union[str, List[str]], 
        model: str = "text-embedding-3-small"
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
            
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            usage = response.usage
            
            # Calculate cost (text-embedding-3-small: $0.00002 per 1K tokens)
            cost_per_1k = 0.00002
            total_cost = (usage.total_tokens / 1000) * cost_per_1k
            
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
