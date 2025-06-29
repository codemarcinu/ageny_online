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

    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
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

    async def complete_text(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> str:
        """
        Complete text using OpenAI API (alias for chat with single message).
        
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
