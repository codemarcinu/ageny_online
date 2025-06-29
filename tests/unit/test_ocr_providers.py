import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.core.ocr_providers.azure_vision import AzureVisionProvider, OCRResult
from backend.core.ocr_providers.google_vision import GoogleVisionProvider
from backend.core.ocr_providers.ocr_factory import OCRProviderFactory, OCRProviderType, OCRProviderConfig

class TestAzureVisionProvider:
    """Test cases for Azure Vision provider."""
    
    def test_azure_vision_initialization(self):
        """Test Azure Vision provider initialization."""
        provider = AzureVisionProvider("test-key", "https://test.cognitiveservices.azure.com/")
        
        assert provider.cost_per_1k_transactions == 1.50
        assert provider.region is None
    
    def test_azure_vision_initialization_without_key(self):
        """Test Azure Vision provider initialization without API key."""
        with pytest.raises(ValueError, match="Azure Vision API key and endpoint are required"):
            AzureVisionProvider("", "https://test.cognitiveservices.azure.com/")
    
    def test_azure_vision_initialization_without_endpoint(self):
        """Test Azure Vision provider initialization without endpoint."""
        with pytest.raises(ValueError, match="Azure Vision API key and endpoint are required"):
            AzureVisionProvider("test-key", "")
    
    @pytest.mark.asyncio
    async def test_azure_vision_extract_text(self, mock_ocr_response):
        """Test Azure Vision text extraction."""
        with patch('backend.core.ocr_providers.azure_vision.ComputerVisionClient') as mock_client_class:
            # Setup mock response
            mock_response = Mock()
            mock_response.headers = {"Operation-Location": "https://test.com/operations/123"}
            mock_response.analyze_result = Mock()
            mock_response.analyze_result.read_results = [Mock()]
            mock_response.analyze_result.read_results[0].lines = [Mock()]
            mock_response.analyze_result.read_results[0].lines[0].words = [Mock()]
            mock_response.analyze_result.read_results[0].lines[0].words[0].text = "Sample"
            mock_response.analyze_result.read_results[0].lines[0].words[0].confidence = 0.95
            mock_response.analyze_result.read_results[0].lines[0].bounding_box = [10, 10, 100, 30]
            
            # Create mock client instance
            mock_client_instance = Mock()
            mock_client_instance.read_in_stream = Mock(return_value=mock_response)
            mock_client_instance.get_read_result = Mock(return_value=mock_response)
            mock_client_class.return_value = mock_client_instance
            
            provider = AzureVisionProvider("test-key", "https://test.cognitiveservices.azure.com/")
            
            # Mock the _wait_for_operation method to avoid timeout
            with patch.object(provider, '_wait_for_operation', return_value=mock_response):
                image_data = b"fake_image_data"
                result = await provider.extract_text(image_data)
                
                assert "text" in result
                assert "confidence" in result
                assert "cost" in result
                assert result["provider"] == "azure_vision"
    
    @pytest.mark.asyncio
    async def test_azure_vision_extract_text_batch(self):
        """Test Azure Vision batch text extraction."""
        with patch('backend.core.ocr_providers.azure_vision.ComputerVisionClient') as mock_client:
            # Setup mock response
            mock_response = Mock()
            mock_response.headers = {"Operation-Location": "https://test.com/operations/123"}
            mock_response.analyze_result = Mock()
            mock_response.analyze_result.read_results = [Mock()]
            mock_response.analyze_result.read_results[0].lines = [Mock()]
            mock_response.analyze_result.read_results[0].lines[0].words = [Mock()]
            mock_response.analyze_result.read_results[0].lines[0].words[0].text = "Sample"
            mock_response.analyze_result.read_results[0].lines[0].words[0].confidence = 0.95
            
            mock_client.return_value.read_in_stream.return_value = mock_response
            mock_client.return_value.get_read_result.return_value = mock_response
            
            provider = AzureVisionProvider("test-key", "https://test.cognitiveservices.azure.com/")
            images = [b"fake_image_1", b"fake_image_2"]
            
            results = await provider.extract_text_batch(images)
            
            assert len(results) == 2
            assert all("text" in result for result in results)
            assert all("cost" in result for result in results)
    
    def test_azure_vision_get_supported_languages(self):
        """Test getting supported languages."""
        provider = AzureVisionProvider("test-key", "https://test.cognitiveservices.azure.com/")
        languages = provider.get_supported_languages()
        
        assert "en" in languages
        assert "pl" in languages
        assert "de" in languages
    
    def test_azure_vision_get_cost_info(self):
        """Test getting cost information."""
        provider = AzureVisionProvider("test-key", "https://test.cognitiveservices.azure.com/")
        cost_info = provider.get_cost_info()
        
        assert cost_info["cost_per_1k_transactions"] == 1.50
        assert cost_info["currency"] == "USD"
        assert cost_info["provider"] == "azure_vision"

class TestGoogleVisionProvider:
    """Test cases for Google Vision provider."""
    
    def test_google_vision_initialization(self):
        """Test Google Vision provider initialization."""
        with patch('backend.core.ocr_providers.google_vision.vision.ImageAnnotatorClient') as mock_client:
            provider = GoogleVisionProvider("test-project-id")
            
            assert provider.project_id == "test-project-id"
            assert provider.cost_per_1k_calls == 1.50
    
    def test_google_vision_initialization_without_project_id(self):
        """Test Google Vision provider initialization without project ID."""
        with pytest.raises(ValueError, match="Google Cloud project ID is required"):
            GoogleVisionProvider("")
    
    @pytest.mark.asyncio
    async def test_google_vision_extract_text(self):
        """Test Google Vision text extraction."""
        with patch('backend.core.ocr_providers.google_vision.vision.ImageAnnotatorClient') as mock_client_class:
            with patch('backend.core.ocr_providers.google_vision.types.TextDetectionParams') as mock_config:
                # Setup mock response
                mock_response = Mock()
                mock_response.text_annotations = [Mock(), Mock()]
                mock_response.text_annotations[0].description = "Sample text"
                mock_response.text_annotations[1].description = "Sample"
                mock_response.text_annotations[1].confidence = 0.95
                mock_response.text_annotations[1].bounding_poly = Mock()
                mock_response.text_annotations[1].bounding_poly.vertices = [Mock(), Mock(), Mock(), Mock()]
                for vertex in mock_response.text_annotations[1].bounding_poly.vertices:
                    vertex.x = 10
                    vertex.y = 10
                
                # Create mock client instance
                mock_client_instance = Mock()
                mock_client_instance.annotate_image.return_value = mock_response
                mock_client_class.return_value = mock_client_instance
                
                provider = GoogleVisionProvider("test-project-id")
                image_data = b"fake_image_data"
                
                result = await provider.extract_text(image_data)
                
                assert "text" in result
                assert "confidence" in result
                assert "cost" in result
                assert result["provider"] == "google_vision"
    
    def test_google_vision_get_supported_languages(self):
        """Test getting supported languages."""
        with patch('backend.core.ocr_providers.google_vision.vision.ImageAnnotatorClient') as mock_client:
            provider = GoogleVisionProvider("test-project-id")
            languages = provider.get_supported_languages()
            
            assert "en" in languages
            assert "pl" in languages
            assert "de" in languages
    
    def test_google_vision_get_cost_info(self):
        """Test getting cost information."""
        with patch('backend.core.ocr_providers.google_vision.vision.ImageAnnotatorClient') as mock_client:
            provider = GoogleVisionProvider("test-project-id")
            cost_info = provider.get_cost_info()
            
            assert cost_info["cost_per_1k_calls"] == 1.50
            assert cost_info["currency"] == "USD"
            assert cost_info["provider"] == "google_vision"

class TestOCRProviderFactory:
    """Test cases for OCR provider factory."""
    
    def test_factory_initialization(self):
        """Test factory initialization."""
        factory = OCRProviderFactory()
        
        assert OCRProviderType.AZURE_VISION in factory._providers
        assert OCRProviderType.GOOGLE_VISION in factory._providers
    
    def test_register_provider(self):
        """Test provider registration."""
        factory = OCRProviderFactory()
        
        config = OCRProviderConfig(
            azure_key="test-key",
            azure_endpoint="https://test.cognitiveservices.azure.com/",
            priority=1
        )
        
        factory.register_provider(OCRProviderType.AZURE_VISION, config)
        
        assert OCRProviderType.AZURE_VISION in factory._configs
        assert factory._configs[OCRProviderType.AZURE_VISION] == config
    
    def test_register_invalid_provider(self):
        """Test registering invalid provider type."""
        factory = OCRProviderFactory()
        
        config = OCRProviderConfig(azure_key="test-key", azure_endpoint="https://test.com/")
        
        with pytest.raises(ValueError, match="Unsupported provider type"):
            factory.register_provider("invalid", config)
    
    def test_register_azure_vision_without_key(self):
        """Test registering Azure Vision without required key."""
        factory = OCRProviderFactory()
        
        config = OCRProviderConfig(
            azure_endpoint="https://test.cognitiveservices.azure.com/",
            priority=1
        )
        
        with pytest.raises(ValueError, match="Azure Vision requires api_key and endpoint"):
            factory.register_provider(OCRProviderType.AZURE_VISION, config)
    
    def test_register_google_vision_without_project_id(self):
        """Test registering Google Vision without project ID."""
        factory = OCRProviderFactory()
        
        config = OCRProviderConfig(priority=1)
        
        with pytest.raises(ValueError, match="Google Vision requires project_id"):
            factory.register_provider(OCRProviderType.GOOGLE_VISION, config)
    
    @pytest.mark.asyncio
    async def test_extract_text_with_fallback(self):
        """Test text extraction with fallback mechanism."""
        factory = OCRProviderFactory()
        
        # Register providers
        factory.register_provider(
            OCRProviderType.AZURE_VISION,
            OCRProviderConfig(
                azure_key="test-key",
                azure_endpoint="https://test.cognitiveservices.azure.com/",
                priority=1
            )
        )
        factory.register_provider(
            OCRProviderType.GOOGLE_VISION,
            OCRProviderConfig(
                google_project_id="test-project",
                priority=2
            )
        )
        
        with patch.object(factory, 'get_provider') as mock_get_provider:
            # Mock provider that succeeds
            mock_provider = Mock()
            mock_provider.extract_text = AsyncMock(return_value={
                "text": "Extracted text",
                "confidence": 0.95,
                "cost": 0.0015,
                "provider": "azure_vision"
            })
            mock_get_provider.return_value = mock_provider
            
            image_data = b"fake_image_data"
            result = await factory.extract_text_with_fallback(image_data)
            
            assert result["text"] == "Extracted text"
            assert result["provider"] == "azure_vision"
    
    @pytest.mark.asyncio
    async def test_extract_text_with_fallback_all_fail(self):
        """Test text extraction with fallback when all providers fail."""
        factory = OCRProviderFactory()
        
        # Register providers
        factory.register_provider(
            OCRProviderType.AZURE_VISION,
            OCRProviderConfig(
                azure_key="test-key",
                azure_endpoint="https://test.cognitiveservices.azure.com/",
                priority=1
            )
        )
        
        with patch.object(factory, 'get_provider') as mock_get_provider:
            # Mock provider that fails
            mock_provider = Mock()
            mock_provider.extract_text = AsyncMock(side_effect=Exception("API Error"))
            mock_get_provider.return_value = mock_provider
            
            image_data = b"fake_image_data"
            
            with pytest.raises(RuntimeError, match="All OCR providers failed"):
                await factory.extract_text_with_fallback(image_data)
    
    def test_adapt_params_for_provider(self):
        """Test parameter adaptation for different providers."""
        factory = OCRProviderFactory()
        
        # Test Azure Vision parameter adaptation
        params = factory._adapt_params_for_provider(
            OCRProviderType.AZURE_VISION,
            language_hints=["en", "pl"],
            max_results=10
        )
        assert params["language"] == "en"
        assert params["max_results"] == 10
        
        # Test Google Vision parameter adaptation
        params = factory._adapt_params_for_provider(
            OCRProviderType.GOOGLE_VISION,
            language_hints=["en", "pl"],
            max_results=10
        )
        assert params["language_hints"] == ["en", "pl"]
        assert params["max_results"] == 10
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        factory = OCRProviderFactory()
        
        # No providers registered
        assert factory.get_available_providers() == []
        
        # Register providers
        factory.register_provider(
            OCRProviderType.AZURE_VISION,
            OCRProviderConfig(
                azure_key="test-key",
                azure_endpoint="https://test.cognitiveservices.azure.com/",
                priority=1
            )
        )
        factory.register_provider(
            OCRProviderType.GOOGLE_VISION,
            OCRProviderConfig(
                google_project_id="test-project",
                priority=2
            )
        )
        
        providers = factory.get_available_providers()
        assert "azure_vision" in providers
        assert "google_vision" in providers
        assert providers[0] == "azure_vision"  # Higher priority first
    
    def test_get_provider_status(self):
        """Test getting provider status."""
        factory = OCRProviderFactory()
        
        status = factory.get_provider_status()
        
        assert status["azure_vision"] == False
        assert status["google_vision"] == False
        
        # Register a provider
        factory.register_provider(
            OCRProviderType.AZURE_VISION,
            OCRProviderConfig(
                azure_key="test-key",
                azure_endpoint="https://test.cognitiveservices.azure.com/"
            )
        )
        
        status = factory.get_provider_status()
        assert status["azure_vision"] == True
        assert status["google_vision"] == False
    
    def test_get_supported_languages(self):
        """Test getting all supported languages across providers."""
        factory = OCRProviderFactory()
        
        # No providers registered
        languages = factory.get_supported_languages()
        assert len(languages) == 0
        
        # Register providers
        factory.register_provider(
            OCRProviderType.AZURE_VISION,
            OCRProviderConfig(
                azure_key="test-key",
                azure_endpoint="https://test.cognitiveservices.azure.com/"
            )
        )
        
        with patch.object(factory, 'get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_supported_languages.return_value = ["en", "pl", "de"]
            mock_get_provider.return_value = mock_provider
            
            languages = factory.get_supported_languages()
            assert "en" in languages
            assert "pl" in languages
            assert "de" in languages 