"""
Provider Factory for LLM providers.
Zapewnia centralne zarządzanie różnymi providerami LLM.
"""

import logging
from enum import Enum
from typing import Dict, Type, Optional, Any

from backend.config import settings

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Available LLM provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    MISTRAL = "mistral"


class BaseLLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
    
    async def chat(self, messages: list, **kwargs: Any) -> str:
        """Generate chat completion"""
        raise NotImplementedError
    
    async def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings"""
        raise NotImplementedError
    
    async def health_check(self) -> dict[str, Any]:
        """Check provider health"""
        raise NotImplementedError


class LLMProviderFactory:
    """
    Factory for creating LLM providers.
    Zapewnia centralne zarządzanie różnymi providerami LLM.
    """
    
    _providers: Dict[ProviderType, Type[BaseLLMProvider]] = {}
    _instances: Dict[ProviderType, BaseLLMProvider] = {}
    
    @classmethod
    def register_provider(cls, provider_type: ProviderType, provider_class: Type[BaseLLMProvider]) -> None:
        """Register a new provider type"""
        cls._providers[provider_type] = provider_class
        logger.info(f"Registered provider: {provider_type}")
    
    @classmethod
    def create_provider(cls, provider_type: ProviderType, api_key: Optional[str] = None) -> BaseLLMProvider:
        """
        Create a provider instance.
        
        Args:
            provider_type: Type of provider to create
            api_key: API key for the provider (optional, will use settings if not provided)
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        # Use singleton pattern for provider instances
        if provider_type not in cls._instances:
            provider_class = cls._providers[provider_type]
            
            # Get API key from settings if not provided
            if not api_key:
                api_key = cls._get_api_key_for_provider(provider_type)
            
            if not api_key:
                raise ValueError(f"API key required for provider: {provider_type}")
            
            cls._instances[provider_type] = provider_class(api_key)
            logger.info(f"Created provider instance: {provider_type}")
        
        return cls._instances[provider_type]
    
    @classmethod
    def _get_api_key_for_provider(cls, provider_type: ProviderType) -> Optional[str]:
        """Get API key for provider from settings"""
        api_key_map = {
            ProviderType.OPENAI: settings.OPENAI_API_KEY,
            ProviderType.ANTHROPIC: settings.ANTHROPIC_API_KEY,
            ProviderType.COHERE: settings.COHERE_API_KEY,
            ProviderType.MISTRAL: settings.MISTRAL_API_KEY,
        }
        return api_key_map.get(provider_type)
    
    @classmethod
    def get_available_providers(cls) -> list[ProviderType]:
        """Get list of available provider types"""
        return list(cls._providers.keys())
    
    @classmethod
    def get_configured_providers(cls) -> list[ProviderType]:
        """Get list of configured providers (with API keys)"""
        configured = []
        for provider_type in cls._providers:
            api_key = cls._get_api_key_for_provider(provider_type)
            if api_key:
                configured.append(provider_type)
        return configured
    
    @classmethod
    def get_provider_priority(cls, provider_type: ProviderType) -> int:
        """Get priority for provider (lower number = higher priority)"""
        priority_map = {
            ProviderType.OPENAI: settings.PROVIDER_PRIORITY_OPENAI,
            ProviderType.ANTHROPIC: settings.PROVIDER_PRIORITY_ANTHROPIC,
            ProviderType.COHERE: settings.PROVIDER_PRIORITY_COHERE,
            ProviderType.MISTRAL: settings.PROVIDER_PRIORITY_MISTRAL,
        }
        return priority_map.get(provider_type, 999)
    
    @classmethod
    def get_best_provider(cls, task_type: str = "chat") -> Optional[ProviderType]:
        """
        Get the best available provider for a task.
        
        Args:
            task_type: Type of task ("chat" or "embed")
            
        Returns:
            Best provider type or None if none available
        """
        configured_providers = cls.get_configured_providers()
        
        if not configured_providers:
            return None
        
        # Sort by priority (lower number = higher priority)
        sorted_providers = sorted(
            configured_providers,
            key=lambda p: cls.get_provider_priority(p)
        )
        
        # For now, return the highest priority provider
        # In the future, this could be more sophisticated based on task type
        return sorted_providers[0] if sorted_providers else None
    
    @classmethod
    async def health_check_all(cls) -> dict[str, Any]:
        """Check health of all configured providers"""
        results = {}
        
        for provider_type in cls.get_configured_providers():
            try:
                provider = cls.create_provider(provider_type)
                health = await provider.health_check()
                results[provider_type.value] = health
            except Exception as e:
                logger.error(f"Health check failed for {provider_type}: {e}")
                results[provider_type.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results


# Import and register providers
try:
    from .openai_client import OpenAIProvider
    LLMProviderFactory.register_provider(ProviderType.OPENAI, OpenAIProvider)
except ImportError:
    logger.warning("OpenAI provider not available")

try:
    from .anthropic_client import AnthropicProvider
    LLMProviderFactory.register_provider(ProviderType.ANTHROPIC, AnthropicProvider)
except ImportError:
    logger.warning("Anthropic provider not available")

try:
    from .cohere_client import CohereProvider
    LLMProviderFactory.register_provider(ProviderType.COHERE, CohereProvider)
except ImportError:
    logger.warning("Cohere provider not available")

try:
    from .mistral_client import MistralProvider
    LLMProviderFactory.register_provider(ProviderType.MISTRAL, MistralProvider)
except ImportError:
    logger.warning("Mistral provider not available")


# Create global factory instance
provider_factory = LLMProviderFactory() 