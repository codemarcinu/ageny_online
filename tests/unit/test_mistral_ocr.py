"""
Unit tests for Mistral Vision OCR provider.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image
import io

from backend.core.ocr_providers.mistral_vision import MistralVisionOCR


class TestMistralVisionOCR:
    """Test cases for MistralVisionOCR provider"""

    @pytest.fixture
    def mock_image_bytes(self):
        """Create mock image bytes"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()

    @pytest.fixture
    def mistral_ocr(self):
        """Create MistralVisionOCR instance with mock API key"""
        return MistralVisionOCR(api_key="test_api_key")

    def test_init(self):
        """Test MistralVisionOCR initialization"""
        ocr = MistralVisionOCR(api_key="test_key")
        assert ocr.api_key == "test_key"
        assert ocr.base_url == "https://api.mistral.ai/v1"
        assert ocr.default_model == "mistral-large-latest"
        assert len(ocr.models) == 3

    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        with pytest.raises(ValueError, match="Mistral API key is required"):
            MistralVisionOCR(api_key="")

    def test_get_model_info(self, mistral_ocr):
        """Test getting model information"""
        model_info = mistral_ocr.get_model_info("mistral-large-latest")
        assert model_info is not None
        assert model_info.model_name == "mistral-large-latest"
        assert model_info.max_tokens == 4096
        assert model_info.supports_vision is True

        # Test non-existent model
        model_info = mistral_ocr.get_model_info("non-existent-model")
        assert model_info is None

    def test_get_available_models(self, mistral_ocr):
        """Test getting available models"""
        models = mistral_ocr.get_available_models()
        assert len(models) == 3
        assert "mistral-large-latest" in models
        assert "mistral-medium-latest" in models
        assert "mistral-small-latest" in models

    def test_calculate_cost(self, mistral_ocr):
        """Test cost calculation"""
        cost = mistral_ocr.calculate_cost("mistral-large-latest", 1000, 500)
        expected_cost = (1000 / 1000) * 0.007 + (500 / 1000) * 0.024
        assert cost == expected_cost

        # Test with non-existent model
        cost = mistral_ocr.calculate_cost("non-existent-model", 1000, 500)
        assert cost == 0.0

    @pytest.mark.asyncio
    async def test_extract_text_success(self, mistral_ocr, mock_image_bytes):
        """Test successful text extraction"""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Extracted text from image"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

        with patch.object(mistral_ocr.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await mistral_ocr.extract_text(mock_image_bytes)

            assert result["text"] == "Extracted text from image"
            assert result["confidence"] == 0.95
            assert result["model_used"] == "mistral-large-latest"
            assert result["tokens_used"] == 150
            assert "cost" in result
            assert "metadata" in result

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://api.mistral.ai/v1/chat/completions"
            
            payload = call_args[1]["json"]
            assert payload["model"] == "mistral-large-latest"
            assert len(payload["messages"]) == 1
            assert payload["messages"][0]["role"] == "user"
            assert len(payload["messages"][0]["content"]) == 2

    @pytest.mark.asyncio
    async def test_extract_text_with_custom_prompt(self, mistral_ocr, mock_image_bytes):
        """Test text extraction with custom prompt"""
        custom_prompt = "Custom OCR prompt"
        mock_response = {
            "choices": [{"message": {"content": "Custom result"}}],
            "usage": {"total_tokens": 100}
        }

        with patch.object(mistral_ocr.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await mistral_ocr.extract_text(mock_image_bytes, prompt=custom_prompt)

            # Verify custom prompt was used
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["messages"][0]["content"][0]["text"] == custom_prompt

    @pytest.mark.asyncio
    async def test_extract_text_api_error(self, mistral_ocr, mock_image_bytes):
        """Test text extraction with API error"""
        with patch.object(mistral_ocr.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.text = "Bad Request"

            with pytest.raises(Exception, match="Mistral Vision API error: 400"):
                await mistral_ocr.extract_text(mock_image_bytes)

    @pytest.mark.asyncio
    async def test_extract_text_batch(self, mistral_ocr, mock_image_bytes):
        """Test batch text extraction"""
        mock_response = {
            "choices": [{"message": {"content": "Batch result"}}],
            "usage": {"total_tokens": 100}
        }

        with patch.object(mistral_ocr.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            images = [mock_image_bytes, mock_image_bytes]
            results = await mistral_ocr.extract_text_batch(images)

            assert len(results) == 2
            for result in results:
                assert result["text"] == "Batch result"
                assert result["image_index"] in [0, 1]

    @pytest.mark.asyncio
    async def test_extract_text_batch_with_error(self, mistral_ocr, mock_image_bytes):
        """Test batch text extraction with one error"""
        mock_response = {
            "choices": [{"message": {"content": "Success result"}}],
            "usage": {"total_tokens": 100}
        }

        with patch.object(mistral_ocr.http_client, 'post', new_callable=AsyncMock) as mock_post:
            # First call succeeds, second call fails
            mock_post.side_effect = [
                MagicMock(status_code=200, json=lambda: mock_response),
                MagicMock(status_code=400, text="Bad Request")
            ]

            images = [mock_image_bytes, mock_image_bytes]
            results = await mistral_ocr.extract_text_batch(images)

            assert len(results) == 2
            assert results[0]["text"] == "Success result"
            assert results[1]["text"] == ""
            assert "error" in results[1]["metadata"]

    @pytest.mark.asyncio
    async def test_analyze_image(self, mistral_ocr, mock_image_bytes):
        """Test image analysis"""
        analysis_prompt = "Analyze this image"
        mock_response = {
            "choices": [{"message": {"content": "Image analysis result"}}],
            "usage": {"total_tokens": 100}
        }

        with patch.object(mistral_ocr.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await mistral_ocr.analyze_image(mock_image_bytes, analysis_prompt)

            assert result["analysis"] == "Image analysis result"
            assert result["model_used"] == "mistral-large-latest"
            assert "cost" in result

    @pytest.mark.asyncio
    async def test_health_check_success(self, mistral_ocr):
        """Test successful health check"""
        mock_response = {
            "data": [
                {"id": "mistral-large-latest"},
                {"id": "mistral-medium-latest"}
            ]
        }

        with patch.object(mistral_ocr.http_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = await mistral_ocr.health_check()

            assert result["status"] == "healthy"
            assert result["models_count"] == 2
            assert "mistral-large-latest" in result["available_models"]

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mistral_ocr):
        """Test health check failure"""
        with patch.object(mistral_ocr.http_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.status_code = 401

            result = await mistral_ocr.health_check()

            assert result["status"] == "unhealthy"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_close(self, mistral_ocr):
        """Test closing HTTP client"""
        with patch.object(mistral_ocr.http_client, 'aclose', new_callable=AsyncMock) as mock_close:
            await mistral_ocr.close()
            mock_close.assert_called_once() 