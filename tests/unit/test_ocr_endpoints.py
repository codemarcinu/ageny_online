"""
Unit tests for OCR API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from PIL import Image
import io

from backend.api.main import app


class TestOCREndpoints:
    """Test cases for OCR API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_image_file(self):
        """Create mock image file"""
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes

    @pytest.fixture
    def mock_ocr_result(self):
        """Create mock OCR result"""
        return {
            "text": "Extracted text from image",
            "confidence": 0.95,
            "model_used": "mistral-large-latest",
            "tokens_used": 150,
            "cost": 0.001,
            "metadata": {"provider": "mistral_vision"}
        }

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_success(self, mock_factory, client, mock_image_file, mock_ocr_result):
        """Test successful text extraction"""
        # Mock provider factory
        mock_provider = AsyncMock()
        mock_provider.extract_text.return_value = mock_ocr_result
        mock_factory.get_best_provider.return_value = "mistral_vision"
        mock_factory.create_provider.return_value = mock_provider

        # Make request
        files = {"file": ("test.jpg", mock_image_file, "image/jpeg")}
        data = {"provider": "mistral_vision"}
        
        response = client.post("/api/v2/ocr/extract-text", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["text"] == "Extracted text from image"
        assert result["confidence"] == 0.95
        assert result["provider"] == "mistral_vision"

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_invalid_file_type(self, mock_factory, client):
        """Test text extraction with invalid file type"""
        # Create text file instead of image
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        
        response = client.post("/api/v2/ocr/extract-text", files=files)
        
        assert response.status_code == 400
        assert "Only image files are supported" in response.json()["detail"]

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_invalid_provider(self, mock_factory, client, mock_image_file):
        """Test text extraction with invalid provider"""
        files = {"file": ("test.jpg", mock_image_file, "image/jpeg")}
        data = {"provider": "invalid_provider"}
        
        response = client.post("/api/v2/ocr/extract-text", files=files, data=data)
        
        assert response.status_code == 400
        assert "Unsupported provider" in response.json()["detail"]

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_no_providers_configured(self, mock_factory, client, mock_image_file):
        """Test text extraction when no providers configured"""
        mock_factory.get_best_provider.return_value = None
        
        files = {"file": ("test.jpg", mock_image_file, "image/jpeg")}
        
        response = client.post("/api/v2/ocr/extract-text", files=files)
        
        assert response.status_code == 503
        assert "No OCR providers configured" in response.json()["detail"]

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_with_custom_prompt(self, mock_factory, client, mock_image_file, mock_ocr_result):
        """Test text extraction with custom prompt"""
        mock_provider = AsyncMock()
        mock_provider.extract_text.return_value = mock_ocr_result
        mock_factory.get_best_provider.return_value = "mistral_vision"
        mock_factory.create_provider.return_value = mock_provider

        files = {"file": ("test.jpg", mock_image_file, "image/jpeg")}
        data = {"prompt": "Custom OCR prompt"}
        
        response = client.post("/api/v2/ocr/extract-text", files=files, data=data)
        
        assert response.status_code == 200
        # Verify custom prompt was passed to provider
        mock_provider.extract_text.assert_called_once()
        call_args = mock_provider.extract_text.call_args
        assert call_args[1]["prompt"] == "Custom OCR prompt"

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_batch_success(self, mock_factory, client, mock_image_file):
        """Test successful batch text extraction"""
        mock_results = [
            {
                "text": f"Text {i}",
                "confidence": 0.9,
                "model_used": "mistral-large-latest",
                "tokens_used": 100,
                "cost": 0.001,
                "metadata": {"provider": "mistral_vision"}
            }
            for i in range(2)
        ]
        
        mock_provider = AsyncMock()
        mock_provider.extract_text_batch.return_value = mock_results
        mock_factory.get_best_provider.return_value = "mistral_vision"
        mock_factory.create_provider.return_value = mock_provider

        files = [
            ("files", ("test1.jpg", mock_image_file, "image/jpeg")),
            ("files", ("test2.jpg", mock_image_file, "image/jpeg"))
        ]
        
        response = client.post("/api/v2/ocr/extract-text-batch", files=files)
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["results"]) == 2
        assert result["total_cost"] == 0.002
        assert result["total_tokens"] == 200

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_batch_too_many_files(self, mock_factory, client, mock_image_file):
        """Test batch extraction with too many files"""
        files = [
            ("files", ("test.jpg", mock_image_file, "image/jpeg"))
            for _ in range(11)  # More than 10 files
        ]
        
        response = client.post("/api/v2/ocr/extract-text-batch", files=files)
        
        assert response.status_code == 400
        assert "Maximum 10 files allowed" in response.json()["detail"]

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_extract_text_batch_with_errors(self, mock_factory, client, mock_image_file):
        """Test batch extraction with some errors"""
        mock_results = [
            {
                "text": "Success text",
                "confidence": 0.9,
                "model_used": "mistral-large-latest",
                "tokens_used": 100,
                "cost": 0.001,
                "metadata": {"provider": "mistral_vision"}
            },
            {
                "text": "",
                "confidence": 0,
                "error": "Processing failed",
                "metadata": {"provider": "mistral_vision", "error": "Processing failed"}
            }
        ]
        
        mock_provider = AsyncMock()
        mock_provider.extract_text_batch.return_value = mock_results
        mock_factory.get_best_provider.return_value = "mistral_vision"
        mock_factory.create_provider.return_value = mock_provider

        files = [
            ("files", ("test1.jpg", mock_image_file, "image/jpeg")),
            ("files", ("test2.jpg", mock_image_file, "image/jpeg"))
        ]
        
        response = client.post("/api/v2/ocr/extract-text-batch", files=files)
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["results"]) == 2
        assert result["results"][0]["text"] == "Success text"
        assert result["results"][1]["text"] == ""
        assert "error" in result["results"][1]["metadata"]

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_get_available_providers(self, mock_factory, client):
        """Test getting available providers"""
        mock_factory.get_available_providers.return_value = ["mistral_vision", "azure_vision"]
        mock_factory.get_configured_providers.return_value = ["mistral_vision"]
        mock_factory.get_provider_priority.return_value = 1
        mock_factory.get_best_provider.return_value = "mistral_vision"
        
        response = client.get("/api/v2/ocr/providers")
        
        assert response.status_code == 200
        result = response.json()
        assert "providers" in result
        assert "best_provider" in result
        assert result["best_provider"] == "mistral_vision"
        assert result["configured_count"] == 1

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_health_check(self, mock_factory, client):
        """Test OCR health check"""
        mock_health_results = {
            "mistral_vision": {
                "status": "healthy",
                "models_count": 3,
                "available_models": ["mistral-large-latest"]
            }
        }
        mock_factory.health_check_all.return_value = mock_health_results
        
        response = client.get("/api/v2/ocr/health")
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "healthy"
        assert "providers" in result
        assert "mistral_vision" in result["providers"]

    @patch('backend.api.v2.endpoints.ocr.ocr_provider_factory')
    def test_health_check_unhealthy(self, mock_factory, client):
        """Test OCR health check when unhealthy"""
        mock_health_results = {
            "mistral_vision": {
                "status": "unhealthy",
                "error": "API key invalid"
            }
        }
        mock_factory.health_check_all.return_value = mock_health_results
        
        response = client.get("/api/v2/ocr/health")
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "unhealthy" 