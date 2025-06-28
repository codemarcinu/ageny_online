"""
Unit tests for OCR Provider Factory.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.core.ocr_providers.ocr_factory import (
    OCRProviderFactory, 
    OCRProviderType, 
    BaseOCRProvider
)


class MockOCRProvider(BaseOCRProvider):
    """Mock OCR provider for testing"""
    
    async def extract_text(self, image_bytes, **kwargs):
        return {
            "text": "Mock extracted text",
            "confidence": 0.9,
            "model_used": "mock-model",
            "tokens_used": 100,
            "cost": 0.001,
            "metadata": {"provider": "mock"}
        }
    
    async def extract_text_batch(self, images, **kwargs):
        results = []
        for i, _ in enumerate(images):
            results.append({
                "text": f"Mock text {i}",
                "confidence": 0.9,
                "image_index": i,
                "metadata": {"provider": "mock"}
            })
        return results
    
    async def health_check(self):
        return {
            "status": "healthy",
            "provider": "mock",
            "models_count": 1
        }


class TestOCRProviderFactory:
    """Test cases for OCRProviderFactory"""

    def setup_method(self):
        """Reset factory state before each test"""
        OCRProviderFactory._providers.clear()
        OCRProviderFactory._instances.clear()

    def test_register_provider(self):
        """Test provider registration"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        assert OCRProviderType.MISTRAL_VISION in OCRProviderFactory._providers
        assert OCRProviderFactory._providers[OCRProviderType.MISTRAL_VISION] == MockOCRProvider

    def test_create_provider_success(self):
        """Test successful provider creation"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = "test_key"
            
            provider = OCRProviderFactory.create_provider(OCRProviderType.MISTRAL_VISION)
            
            assert isinstance(provider, MockOCRProvider)
            assert provider.api_key == "test_key"

    def test_create_provider_with_custom_api_key(self):
        """Test provider creation with custom API key"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        provider = OCRProviderFactory.create_provider(
            OCRProviderType.MISTRAL_VISION, 
            api_key="custom_key"
        )
        
        assert isinstance(provider, MockOCRProvider)
        assert provider.api_key == "custom_key"

    def test_create_provider_unregistered(self):
        """Test creating unregistered provider"""
        with pytest.raises(ValueError, match="Unsupported OCR provider"):
            OCRProviderFactory.create_provider(OCRProviderType.MISTRAL_VISION)

    def test_create_provider_no_api_key(self):
        """Test creating provider without API key"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = ""
            
            with pytest.raises(ValueError, match="API key required"):
                OCRProviderFactory.create_provider(OCRProviderType.MISTRAL_VISION)

    def test_singleton_pattern(self):
        """Test that provider instances are singletons"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = "test_key"
            
            provider1 = OCRProviderFactory.create_provider(OCRProviderType.MISTRAL_VISION)
            provider2 = OCRProviderFactory.create_provider(OCRProviderType.MISTRAL_VISION)
            
            assert provider1 is provider2

    def test_get_available_providers(self):
        """Test getting available providers"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        providers = OCRProviderFactory.get_available_providers()
        assert OCRProviderType.MISTRAL_VISION in providers

    def test_get_configured_providers(self):
        """Test getting configured providers"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = "test_key"
            mock_settings.AZURE_VISION_KEY = ""
            mock_settings.GOOGLE_VISION_CREDENTIALS_PATH = ""
            
            configured = OCRProviderFactory.get_configured_providers()
            assert OCRProviderType.MISTRAL_VISION in configured
            assert len(configured) == 1

    def test_get_provider_priority(self):
        """Test getting provider priority"""
        priority = OCRProviderFactory.get_provider_priority(OCRProviderType.MISTRAL_VISION)
        assert priority == 1  # Highest priority
        
        priority = OCRProviderFactory.get_provider_priority(OCRProviderType.AZURE_VISION)
        assert priority == 2
        
        priority = OCRProviderFactory.get_provider_priority(OCRProviderType.GOOGLE_VISION)
        assert priority == 3

    def test_get_best_provider(self):
        """Test getting best available provider"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        OCRProviderFactory.register_provider(OCRProviderType.AZURE_VISION, MockOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = "test_key"
            mock_settings.AZURE_VISION_KEY = "test_key"
            
            best_provider = OCRProviderFactory.get_best_provider()
            assert best_provider == OCRProviderType.MISTRAL_VISION  # Highest priority

    def test_get_best_provider_none_configured(self):
        """Test getting best provider when none configured"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = ""
            
            best_provider = OCRProviderFactory.get_best_provider()
            assert best_provider is None

    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """Test health check for all providers"""
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, MockOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = "test_key"
            
            results = await OCRProviderFactory.health_check_all()
            
            assert "mistral_vision" in results
            assert results["mistral_vision"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_all_with_error(self):
        """Test health check with provider error"""
        class ErrorOCRProvider(MockOCRProvider):
            async def health_check(self):
                raise Exception("Health check failed")
        
        OCRProviderFactory.register_provider(OCRProviderType.MISTRAL_VISION, ErrorOCRProvider)
        
        with patch('backend.core.ocr_providers.ocr_factory.settings') as mock_settings:
            mock_settings.MISTRAL_API_KEY = "test_key"
            
            results = await OCRProviderFactory.health_check_all()
            
            assert "mistral_vision" in results
            assert results["mistral_vision"]["status"] == "error"
            assert "Health check failed" in results["mistral_vision"]["error"]


class TestOCRProviderType:
    """Test cases for OCRProviderType enum"""

    def test_provider_types(self):
        """Test available provider types"""
        assert OCRProviderType.MISTRAL_VISION == "mistral_vision"
        assert OCRProviderType.AZURE_VISION == "azure_vision"
        assert OCRProviderType.GOOGLE_VISION == "google_vision"

    def test_provider_type_creation(self):
        """Test creating provider type from string"""
        provider_type = OCRProviderType("mistral_vision")
        assert provider_type == OCRProviderType.MISTRAL_VISION

    def test_invalid_provider_type(self):
        """Test creating invalid provider type"""
        with pytest.raises(ValueError):
            OCRProviderType("invalid_provider") 