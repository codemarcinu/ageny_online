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
    PERPLEXITY = "perplexity"


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
            ValueError: If provider type is not supported or API key is missing
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
            
            try:
                cls._instances[provider_type] = provider_class(api_key)
                logger.info(f"Created provider instance: {provider_type}")
            except Exception as e:
                logger.error(f"Failed to create provider {provider_type}: {e}")
                raise ValueError(f"Failed to create provider {provider_type}: {e}")
        
        return cls._instances[provider_type]
    
    @classmethod
    def _get_api_key_for_provider(cls, provider_type: ProviderType) -> Optional[str]:
        """Get API key for provider from settings"""
        api_key_map = {
            ProviderType.OPENAI: settings.OPENAI_API_KEY,
            ProviderType.ANTHROPIC: settings.ANTHROPIC_API_KEY,
            ProviderType.COHERE: settings.COHERE_API_KEY,
            ProviderType.MISTRAL: settings.MISTRAL_API_KEY,
            ProviderType.PERPLEXITY: settings.PERPLEXITY_API_KEY,
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
            ProviderType.PERPLEXITY: settings.PROVIDER_PRIORITY_PERPLEXITY,
        }
        return priority_map.get(provider_type, 999)
    
    @classmethod
    def get_provider_priorities(cls) -> Dict[str, int]:
        """Get priorities for all available providers"""
        priorities = {}
        for provider_type in cls._providers:
            priorities[provider_type.value] = cls.get_provider_priority(provider_type)
        return priorities
    
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
    
    @classmethod
    def get_provider(cls, provider_type: ProviderType) -> BaseLLMProvider:
        """Get provider instance by type"""
        return cls.create_provider(provider_type)

    @classmethod
    async def chat_with_fallback(
        cls,
        messages: list,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> dict[str, Any]:
        """
        Generate chat completion with automatic fallback to available providers.
        
        Args:
            messages: List of message dictionaries
            model: Model to use (will be adapted per provider if needed)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Chat completion result
            
        Raises:
            Exception: If no providers are available or all providers fail
        """
        configured_providers = cls.get_configured_providers()
        
        if not configured_providers:
            raise Exception("No LLM providers configured")
        
        # Sort by priority (lower number = higher priority)
        sorted_providers = sorted(
            configured_providers,
            key=lambda p: cls.get_provider_priority(p)
        )
        
        last_error = None
        
        # Try each provider in order of priority
        for provider_type in sorted_providers:
            try:
                provider = cls.create_provider(provider_type)
                
                # Adapt model for provider if needed
                adapted_model = cls._adapt_model_for_provider(model, provider_type)
                
                result = await provider.chat(
                    messages=messages,
                    model=adapted_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                # Add provider info to result
                result["provider"] = provider_type.value
                result["model_used"] = adapted_model or "default"
                
                logger.info(f"Chat completion successful with provider: {provider_type.value}")
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_type.value} failed: {e}")
                continue
        
        # If we get here, all providers failed
        error_msg = f"All providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    @classmethod
    def _adapt_model_for_provider(cls, model: Optional[str], provider_type: ProviderType) -> Optional[str]:
        """Adapt model name for specific provider."""
        if not model:
            return None
        
        # Model mapping for different providers
        model_mapping = {
            ProviderType.OPENAI: {
                "gpt-4": "gpt-4o",
                "gpt-3.5": "gpt-3.5-turbo",
                "gpt-4-turbo": "gpt-4o",
                "gpt-4o-mini": "gpt-4o-mini"
            },
            ProviderType.MISTRAL: {
                "gpt-4": "mistral-large-latest",
                "gpt-3.5": "mistral-small-latest",
                "gpt-4-turbo": "mistral-large-latest",
                "gpt-4o-mini": "mistral-small-latest"
            },
            ProviderType.PERPLEXITY: {
                "gpt-4": "sonar-pro",
                "gpt-3.5": "sonar-small-online",
                "gpt-4-turbo": "sonar-pro",
                "gpt-4o-mini": "sonar-small-online",
                "search": "sonar-pro-online"
            }
        }
        
        return model_mapping.get(provider_type, {}).get(model, model)


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

try:
    from .perplexity_client import PerplexityProvider
    LLMProviderFactory.register_provider(ProviderType.PERPLEXITY, PerplexityProvider)
except ImportError:
    logger.warning("Perplexity provider not available")

# Ułatwienie importu
provider_factory = LLMProviderFactory
