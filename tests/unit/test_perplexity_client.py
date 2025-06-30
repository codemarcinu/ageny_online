"""
Unit tests for Perplexity API client.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from backend.core.llm_providers.perplexity_client import PerplexityProvider, PerplexityConfig


class TestPerplexityConfig:
    """Test PerplexityConfig class."""
    
    def test_perplexity_config_creation(self):
        """Test PerplexityConfig creation."""
        config = PerplexityConfig(
            model_name="sonar-pro",
            max_tokens=4096,
            temperature=0.1,
            cost_per_1k=0.0002,
            supports_streaming=True,
            supports_search=True
        )
        
        assert config.model_name == "sonar-pro"
        assert config.max_tokens == 4096
        assert config.temperature == 0.1
        assert config.cost_per_1k == 0.0002
        assert config.supports_streaming is True
        assert config.supports_search is True


class TestPerplexityProvider:
    """Test PerplexityProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create PerplexityProvider instance."""
        return PerplexityProvider(api_key="test_key")
    
    def test_provider_initialization(self, provider):
        """Test provider initialization."""
        assert provider.api_key == "test_key"
        assert provider.base_url == "https://api.perplexity.ai"
        assert "sonar-pro" in provider.models
        assert "sonar-pro-online" in provider.models
        assert "sonar-small-online" in provider.models
        assert "llama-3.1-8b-online" in provider.models
    
    def test_calculate_cost(self, provider):
        """Test cost calculation."""
        # Test sonar-pro cost
        cost = provider.calculate_cost("sonar-pro", 1000)
        assert cost == 0.0002  # $0.20 per 1M tokens
        
        # Test sonar-small-online cost
        cost = provider.calculate_cost("sonar-small-online", 1000)
        assert cost == 0.0001  # $0.10 per 1M tokens
        
        # Test unknown model
        cost = provider.calculate_cost("unknown-model", 1000)
        assert cost == 0.0
    
    @pytest.mark.asyncio
    async def test_chat_success(self, provider):
        """Test successful chat completion."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "Test response"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        
        with patch.object(provider.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await provider.chat(
                messages=[{"role": "user", "content": "Hello"}],
                model="sonar-pro"
            )
            
            assert result["text"] == "Test response"
            assert result["model"] == "sonar-pro"
            assert result["provider"] == "perplexity"
            assert result["finish_reason"] == "stop"
            assert "usage" in result
            assert "cost" in result
    
    @pytest.mark.asyncio
    async def test_chat_api_error(self, provider):
        """Test chat completion with API error."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch.object(provider.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception, match="Perplexity API error: 400"):
                await provider.chat(
                    messages=[{"role": "user", "content": "Hello"}]
                )
    
    @pytest.mark.asyncio
    async def test_chat_no_choices(self, provider):
        """Test chat completion with no choices in response."""
        # Mock response with no choices
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []}
        
        with patch.object(provider.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception, match="No choices in Perplexity response"):
                await provider.chat(
                    messages=[{"role": "user", "content": "Hello"}]
                )
    
    @pytest.mark.asyncio
    async def test_search_success(self, provider):
        """Test successful search."""
        # Mock chat method
        with patch.object(provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "text": "Search results for test query",
                "model": "sonar-pro-online",
                "provider": "perplexity"
            }
            
            result = await provider.search(
                query="test query",
                model="sonar-pro-online"
            )
            
            assert result["text"] == "Search results for test query"
            assert result["model"] == "sonar-pro-online"
            assert result["provider"] == "perplexity"
            
            # Verify chat was called with correct parameters
            mock_chat.assert_called_once()
            # Check that chat was called with the right model
            assert mock_chat.call_args[1]["model"] == "sonar-pro-online"
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, provider):
        """Test search with filters."""
        with patch.object(provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {"text": "Filtered results"}
            
            await provider.search(
                query="test query",
                search_domain_filter="example.com",
                date_range_filter="2024-01-01:2024-12-31",
                academic_filter=True
            )
            
            # Verify filters were passed to chat
            call_args = mock_chat.call_args[1]
            assert call_args["search_domain_filter"] == "example.com"
            assert call_args["date_range_filter"] == "2024-01-01:2024-12-31"
            assert call_args["academic_filter"] is True
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, provider):
        """Test successful health check."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "sonar-pro"},
                {"id": "sonar-pro-online"}
            ]
        }
        
        with patch.object(provider.http_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            result = await provider.health_check()
            
            assert result["status"] == "healthy"
            assert result["provider"] == "perplexity"
            assert result["models_available"] == 2
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, provider):
        """Test health check failure."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(provider.http_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            result = await provider.health_check()
            
            assert result["status"] == "unhealthy"
            assert result["provider"] == "perplexity"
            assert "HTTP 500" in result["error"]
    
    @pytest.mark.asyncio
    async def test_health_check_exception(self, provider):
        """Test health check with exception."""
        with patch.object(provider.http_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            result = await provider.health_check()
            
            assert result["status"] == "unhealthy"
            assert result["provider"] == "perplexity"
            assert "Connection error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_close_client(self, provider):
        """Test closing HTTP client."""
        with patch.object(provider.http_client, 'aclose', new_callable=AsyncMock) as mock_close:
            await provider.close()
            mock_close.assert_called_once() 