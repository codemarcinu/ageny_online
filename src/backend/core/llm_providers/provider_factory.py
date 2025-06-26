import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Type, Optional, List, Any
from dataclasses import dataclass

from .openai_client import OpenAIProvider
from .mistral_client import MistralProvider

logger = logging.getLogger(__name__)

class ProviderType(Enum):
    """Available LLM provider types."""
    OPENAI = "openai"
    MISTRAL = "mistral"

@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    api_key: str
    organization: Optional[str] = None
    priority: int = 1  # Lower number = higher priority

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        pass
    
    @abstractmethod
    async def embed(
        self, 
        texts: Any, 
        model: str = None
    ) -> Dict[str, Any]:
        """Generate embeddings."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass

class LLMProviderFactory:
    """Factory for creating and managing LLM providers."""
    
    def __init__(self):
        self._providers: Dict[ProviderType, Type[BaseLLMProvider]] = {
            ProviderType.OPENAI: OpenAIProvider,
            ProviderType.MISTRAL: MistralProvider,
        }
        self._instances: Dict[ProviderType, BaseLLMProvider] = {}
        self._configs: Dict[ProviderType, ProviderConfig] = {}
        self._fallback_order: List[ProviderType] = []
    
    def register_provider(
        self, 
        provider_type: ProviderType, 
        config: ProviderConfig
    ) -> None:
        """
        Register a provider with its configuration.
        
        Args:
            provider_type: Type of provider to register
            config: Configuration for the provider
        """
        if provider_type not in self._providers:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        self._configs[provider_type] = config
        logger.info(f"Registered provider: {provider_type.value}")
        
        # Update fallback order based on priority
        self._update_fallback_order()
    
    def _update_fallback_order(self) -> None:
        """Update the fallback order based on provider priorities."""
        sorted_configs = sorted(
            self._configs.items(),
            key=lambda x: x[1].priority
        )
        self._fallback_order = [provider_type for provider_type, _ in sorted_configs]
        logger.debug(f"Updated fallback order: {[p.value for p in self._fallback_order]}")
    
    def get_provider(self, provider_type: ProviderType) -> BaseLLMProvider:
        """
        Get or create a provider instance.
        
        Args:
            provider_type: Type of provider to get
            
        Returns:
            Provider instance
        """
        if provider_type not in self._configs:
            raise ValueError(f"Provider {provider_type.value} not configured")
        
        if provider_type not in self._instances:
            config = self._configs[provider_type]
            provider_class = self._providers[provider_type]
            
            if provider_type == ProviderType.OPENAI:
                self._instances[provider_type] = provider_class(
                    api_key=config.api_key,
                    organization=config.organization
                )
            else:
                self._instances[provider_type] = provider_class(
                    api_key=config.api_key
                )
            
            logger.info(f"Created provider instance: {provider_type.value}")
        
        return self._instances[provider_type]
    
    async def chat_with_fallback(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion with automatic fallback to available providers.
        
        Args:
            messages: List of message dictionaries
            model: Model to use (will be adapted per provider if needed)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing response and provider info
        """
        last_error = None
        
        for provider_type in self._fallback_order:
            try:
                provider = self.get_provider(provider_type)
                
                # Adapt model name for provider if needed
                adapted_model = self._adapt_model_for_provider(model, provider_type)
                
                result = await provider.chat(
                    messages=messages,
                    model=adapted_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                # Add provider info to result
                result["provider"] = provider_type.value
                logger.info(f"Chat completion successful with {provider_type.value}")
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_type.value} failed: {e}")
                continue
        
        # All providers failed
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    
    async def embed_with_fallback(
        self,
        texts: Any,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate embeddings with automatic fallback.
        
        Args:
            texts: Text or list of texts to embed
            model: Embedding model to use
            
        Returns:
            Dictionary containing embeddings and provider info
        """
        last_error = None
        
        for provider_type in self._fallback_order:
            try:
                provider = self.get_provider(provider_type)
                
                # Adapt model name for provider if needed
                adapted_model = self._adapt_embedding_model_for_provider(model, provider_type)
                
                result = await provider.embed(
                    texts=texts,
                    model=adapted_model
                )
                
                # Add provider info to result
                result["provider"] = provider_type.value
                logger.info(f"Embeddings generated successfully with {provider_type.value}")
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_type.value} failed: {e}")
                continue
        
        # All providers failed
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    
    def _adapt_model_for_provider(self, model: Optional[str], provider_type: ProviderType) -> Optional[str]:
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
            }
        }
        
        return model_mapping.get(provider_type, {}).get(model, model)
    
    def _adapt_embedding_model_for_provider(self, model: Optional[str], provider_type: ProviderType) -> str:
        """Adapt embedding model name for specific provider."""
        if not model:
            # Return default embedding model for provider
            defaults = {
                ProviderType.OPENAI: "text-embedding-3-small",
                ProviderType.MISTRAL: "mistral-embed"
            }
            return defaults.get(provider_type, "text-embedding-3-small")
        
        # Model mapping for embeddings
        model_mapping = {
            ProviderType.OPENAI: {
                "text-embedding-3-small": "text-embedding-3-small",
                "text-embedding-3-large": "text-embedding-3-large",
                "text-embedding-ada-002": "text-embedding-ada-002"
            },
            ProviderType.MISTRAL: {
                "text-embedding-3-small": "mistral-embed",
                "text-embedding-3-large": "mistral-embed",
                "text-embedding-ada-002": "mistral-embed",
                "mistral-embed": "mistral-embed"
            }
        }
        
        return model_mapping.get(provider_type, {}).get(model, model)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider types."""
        return [provider_type.value for provider_type in self._fallback_order]
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all configured providers."""
        status = {}
        for provider_type in ProviderType:
            status[provider_type.value] = provider_type in self._configs
        return status

# Global factory instance
llm_factory = LLMProviderFactory()
