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