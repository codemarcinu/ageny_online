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
