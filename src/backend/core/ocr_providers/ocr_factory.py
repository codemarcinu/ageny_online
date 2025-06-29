<<<<<<< HEAD
"""
OCR Provider Factory.
Zapewnia centralne zarządzanie różnymi providerami OCR.
"""

import logging
from enum import Enum
from typing import Dict, Type, Optional, Any

from backend.config import settings

logger = logging.getLogger(__name__)


class OCRProviderType(str, Enum):
    """Available OCR provider types"""
    MISTRAL_VISION = "mistral_vision"
    AZURE_VISION = "azure_vision"
    GOOGLE_VISION = "google_vision"


class BaseOCRProvider:
    """Base class for OCR providers"""
    
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
    
    async def extract_text(self, image_bytes: bytes, **kwargs: Any) -> Dict[str, Any]:
        """Extract text from image"""
        raise NotImplementedError
    
    async def extract_text_batch(self, images: list[bytes], **kwargs: Any) -> list[Dict[str, Any]]:
        """Extract text from multiple images"""
        raise NotImplementedError
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        raise NotImplementedError


class OCRProviderFactory:
    """
    Factory for creating OCR providers.
    Zapewnia centralne zarządzanie różnymi providerami OCR.
    """
    
    _providers: Dict[OCRProviderType, Type[BaseOCRProvider]] = {}
    _instances: Dict[OCRProviderType, BaseOCRProvider] = {}
    
    @classmethod
    def register_provider(cls, provider_type: OCRProviderType, provider_class: Type[BaseOCRProvider]) -> None:
        """Register a new provider type"""
        cls._providers[provider_type] = provider_class
        logger.info(f"Registered OCR provider: {provider_type}")
    
    @classmethod
    def create_provider(cls, provider_type: OCRProviderType, api_key: Optional[str] = None) -> BaseOCRProvider:
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
            raise ValueError(f"Unsupported OCR provider: {provider_type}")
        
        # Use singleton pattern for provider instances
        if provider_type not in cls._instances:
            provider_class = cls._providers[provider_type]
            
            # Get API key from settings if not provided
            if not api_key:
                api_key = cls._get_api_key_for_provider(provider_type)
            
            if not api_key:
                raise ValueError(f"API key required for OCR provider: {provider_type}")
            
            cls._instances[provider_type] = provider_class(api_key)
            logger.info(f"Created OCR provider instance: {provider_type}")
        
        return cls._instances[provider_type]
    
    @classmethod
    def _get_api_key_for_provider(cls, provider_type: OCRProviderType) -> Optional[str]:
        """Get API key for provider from settings"""
        api_key_map = {
            OCRProviderType.MISTRAL_VISION: settings.MISTRAL_API_KEY,
            OCRProviderType.AZURE_VISION: settings.AZURE_VISION_KEY,
            OCRProviderType.GOOGLE_VISION: settings.GOOGLE_VISION_CREDENTIALS_PATH,
        }
        return api_key_map.get(provider_type)
    
    @classmethod
    def get_available_providers(cls) -> list[OCRProviderType]:
        """Get list of available provider types"""
        return list(cls._providers.keys())
    
    @classmethod
    def get_configured_providers(cls) -> list[OCRProviderType]:
        """Get list of configured providers (with API keys)"""
        configured = []
        for provider_type in cls._providers:
            api_key = cls._get_api_key_for_provider(provider_type)
            if api_key:
                configured.append(provider_type)
        return configured
    
    @classmethod
    def get_provider_priority(cls, provider_type: OCRProviderType) -> int:
        """Get priority for provider (lower number = higher priority)"""
        priority_map = {
            OCRProviderType.MISTRAL_VISION: 1,  # Highest priority
            OCRProviderType.AZURE_VISION: 2,
            OCRProviderType.GOOGLE_VISION: 3,
        }
        return priority_map.get(provider_type, 999)
    
    @classmethod
    def get_best_provider(cls) -> Optional[OCRProviderType]:
        """
        Get the best available OCR provider.
        
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
        
        return sorted_providers[0] if sorted_providers else None
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, Any]:
        """Check health of all configured providers"""
        results = {}
        
        for provider_type in cls.get_configured_providers():
            try:
                provider = cls.create_provider(provider_type)
                health = await provider.health_check()
                results[provider_type.value] = health
            except Exception as e:
                logger.error(f"OCR health check failed for {provider_type}: {e}")
                results[provider_type.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results


# Import and register providers
try:
    from .mistral_vision import MistralVisionOCR
    OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MistralVisionOCR)
except ImportError:
    logger.warning("Mistral Vision OCR provider not available")

# TODO: Add Azure Vision and Google Vision providers when implemented
# try:
#     from .azure_vision import AzureVisionOCR
#     OCRProviderFactory.register_provider(OCRProviderType.AZURE_VISION, AzureVisionOCR)
# except ImportError:
#     logger.warning("Azure Vision OCR provider not available")

# try:
#     from .google_vision import GoogleVisionOCR
#     OCRProviderFactory.register_provider(OCRProviderType.GOOGLE_VISION, GoogleVisionOCR)
# except ImportError:
#     logger.warning("Google Vision OCR provider not available")


# Create global factory instance
ocr_provider_factory = OCRProviderFactory() 
=======
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Type, Optional, List, Any
from dataclasses import dataclass

from .azure_vision import AzureVisionProvider
from .google_vision import GoogleVisionProvider

logger = logging.getLogger(__name__)

class OCRProviderType(Enum):
    """Available OCR provider types."""
    AZURE_VISION = "azure_vision"
    GOOGLE_VISION = "google_vision"

@dataclass
class OCRProviderConfig:
    """Configuration for an OCR provider."""
    # Azure Vision config
    azure_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_region: Optional[str] = None
    
    # Google Vision config
    google_project_id: Optional[str] = None
    google_credentials_path: Optional[str] = None
    
    priority: int = 1  # Lower number = higher priority

class BaseOCRProvider(ABC):
    """Abstract base class for OCR providers."""
    
    @abstractmethod
    async def extract_text(
        self, 
        image_data: bytes,
        **kwargs
    ) -> Dict[str, Any]:
        """Extract text from image."""
        pass
    
    @abstractmethod
    async def extract_text_batch(
        self, 
        images: List[bytes],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Extract text from multiple images."""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        pass

class OCRProviderFactory:
    """Factory for creating and managing OCR providers."""
    
    def __init__(self):
        self._providers: Dict[OCRProviderType, Type[BaseOCRProvider]] = {
            OCRProviderType.AZURE_VISION: AzureVisionProvider,
            OCRProviderType.GOOGLE_VISION: GoogleVisionProvider,
        }
        self._instances: Dict[OCRProviderType, BaseOCRProvider] = {}
        self._configs: Dict[OCRProviderType, OCRProviderConfig] = {}
        self._fallback_order: List[OCRProviderType] = []
    
    def register_provider(
        self, 
        provider_type: OCRProviderType, 
        config: OCRProviderConfig
    ) -> None:
        """
        Register a provider with its configuration.
        
        Args:
            provider_type: Type of provider to register
            config: Configuration for the provider
        """
        if provider_type not in self._providers:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        # Validate configuration for specific provider
        if provider_type == OCRProviderType.AZURE_VISION:
            if not config.azure_key or not config.azure_endpoint:
                raise ValueError("Azure Vision requires api_key and endpoint")
        elif provider_type == OCRProviderType.GOOGLE_VISION:
            if not config.google_project_id:
                raise ValueError("Google Vision requires project_id")
        
        self._configs[provider_type] = config
        logger.info(f"Registered OCR provider: {provider_type.value}")
        
        # Update fallback order based on priority
        self._update_fallback_order()
    
    def _update_fallback_order(self) -> None:
        """Update the fallback order based on provider priorities."""
        sorted_configs = sorted(
            self._configs.items(),
            key=lambda x: x[1].priority
        )
        self._fallback_order = [provider_type for provider_type, _ in sorted_configs]
        logger.debug(f"Updated OCR fallback order: {[p.value for p in self._fallback_order]}")
    
    def get_provider(self, provider_type: OCRProviderType) -> BaseOCRProvider:
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
            
            if provider_type == OCRProviderType.AZURE_VISION:
                self._instances[provider_type] = provider_class(
                    api_key=config.azure_key,
                    endpoint=config.azure_endpoint,
                    region=config.azure_region
                )
            elif provider_type == OCRProviderType.GOOGLE_VISION:
                self._instances[provider_type] = provider_class(
                    project_id=config.google_project_id,
                    credentials_path=config.google_credentials_path
                )
            
            logger.info(f"Created OCR provider instance: {provider_type.value}")
        
        return self._instances[provider_type]
    
    async def extract_text_with_fallback(
        self,
        image_data: bytes,
        language_hints: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract text from image with automatic fallback to available providers.
        
        Args:
            image_data: Image data as bytes
            language_hints: Language hints for OCR
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing OCR results and provider info
        """
        last_error = None
        
        for provider_type in self._fallback_order:
            try:
                provider = self.get_provider(provider_type)
                
                # Adapt parameters for specific provider
                provider_kwargs = self._adapt_params_for_provider(
                    provider_type, 
                    language_hints, 
                    **kwargs
                )
                
                result = await provider.extract_text(
                    image_data=image_data,
                    **provider_kwargs
                )
                
                logger.info(f"OCR successful with {provider_type.value}")
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"OCR provider {provider_type.value} failed: {e}")
                continue
        
        # All providers failed
        raise RuntimeError(f"All OCR providers failed. Last error: {last_error}")
    
    async def extract_text_batch_with_fallback(
        self,
        images: List[bytes],
        language_hints: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extract text from multiple images with automatic fallback.
        
        Args:
            images: List of image data as bytes
            language_hints: Language hints for OCR
            **kwargs: Additional parameters
            
        Returns:
            List of OCR results
        """
        last_error = None
        
        for provider_type in self._fallback_order:
            try:
                provider = self.get_provider(provider_type)
                
                # Adapt parameters for specific provider
                provider_kwargs = self._adapt_params_for_provider(
                    provider_type, 
                    language_hints, 
                    **kwargs
                )
                
                results = await provider.extract_text_batch(
                    images=images,
                    **provider_kwargs
                )
                
                logger.info(f"Batch OCR successful with {provider_type.value}")
                return results
                
            except Exception as e:
                last_error = e
                logger.warning(f"OCR provider {provider_type.value} failed: {e}")
                continue
        
        # All providers failed
        raise RuntimeError(f"All OCR providers failed. Last error: {last_error}")
    
    def _adapt_params_for_provider(
        self, 
        provider_type: OCRProviderType, 
        language_hints: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Adapt parameters for specific provider."""
        provider_kwargs = kwargs.copy()
        
        if provider_type == OCRProviderType.AZURE_VISION:
            if language_hints:
                provider_kwargs["language"] = language_hints[0] if language_hints else None
        elif provider_type == OCRProviderType.GOOGLE_VISION:
            if language_hints:
                provider_kwargs["language_hints"] = language_hints
        
        return provider_kwargs
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider types."""
        return [provider_type.value for provider_type in self._fallback_order]
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all configured providers."""
        status = {}
        for provider_type in OCRProviderType:
            status[provider_type.value] = provider_type in self._configs
        return status
    
    def get_supported_languages(self) -> List[str]:
        """Get all supported languages across all providers."""
        all_languages = set()
        
        for provider_type in self._fallback_order:
            try:
                provider = self.get_provider(provider_type)
                languages = provider.get_supported_languages()
                all_languages.update(languages)
            except Exception as e:
                logger.warning(f"Could not get languages for {provider_type.value}: {e}")
        
        return sorted(list(all_languages))

# Global factory instance
ocr_factory = OCRProviderFactory() 
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
