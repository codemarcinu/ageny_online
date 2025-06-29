"""
Unit tests for LLM providers.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from backend.core.llm_providers.provider_factory import provider_factory, ProviderType
from backend.core.llm_providers.openai_client import OpenAIProvider
from backend.core.llm_providers.mistral_client import MistralProvider
from backend.core.llm_providers.anthropic_client import AnthropicProvider
from backend.core.llm_providers.cohere_client import CohereProvider

# Mock configuration
MOCK_CONFIG = {
    "openai": {
        "api_key": "test_openai_key",
        "base_url": "https://api.openai.com/v1"
    },
    "mistral": {
        "api_key": "test_mistral_key",
        "base_url": "https://api.mistral.ai/v1"
    },
    "anthropic": {
        "api_key": "test_anthropic_key",
        "base_url": "https://api.anthropic.com"
    },
    "cohere": {
        "api_key": "test_cohere_key",
        "base_url": "https://api.cohere.ai"
    }
}

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('backend.config.settings') as mock_settings:
        mock_settings.openai_api_key = "test_openai_key"
        mock_settings.mistral_api_key = "test_mistral_key"
        mock_settings.anthropic_api_key = "test_anthropic_key"
        mock_settings.cohere_api_key = "test_cohere_key"
        yield mock_settings

@pytest.fixture
def mock_provider_config():
    """Mock provider configuration."""
    def get_provider_config(provider: str) -> Dict[str, Any]:
        return MOCK_CONFIG.get(provider, {})
    
    with patch('backend.config.get_provider_config', side_effect=get_provider_config):
        yield get_provider_config

class TestProviderFactory:
    """Test provider factory functionality."""
    
    def test_get_available_providers(self, mock_settings):
        """Test getting available providers."""
        providers = provider_factory.get_available_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0
        
        # Check that all providers are ProviderType instances
        for provider in providers:
            assert isinstance(provider, ProviderType)
    
    def test_get_provider_openai(self, mock_settings):
        """Test getting OpenAI provider."""
        provider = provider_factory.create_provider(ProviderType.OPENAI)
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "test_openai_key"
    
    def test_get_provider_mistral(self, mock_settings):
        """Test getting Mistral provider."""
        provider = provider_factory.create_provider(ProviderType.MISTRAL)
        assert isinstance(provider, MistralProvider)
        assert provider.api_key == "test_mistral_key"
    
    def test_get_provider_anthropic(self, mock_settings):
        """Test getting Anthropic provider."""
        provider = provider_factory.create_provider(ProviderType.ANTHROPIC)
        assert isinstance(provider, AnthropicProvider)
        assert provider.api_key == "test_anthropic_key"
    
    def test_get_provider_cohere(self, mock_settings):
        """Test getting Cohere provider."""
        provider = provider_factory.create_provider(ProviderType.COHERE)
        assert isinstance(provider, CohereProvider)
        assert provider.api_key == "test_cohere_key"
    
    def test_get_provider_invalid(self, mock_settings):
        """Test getting invalid provider."""
        with pytest.raises(ValueError):
            provider_factory.create_provider("invalid_provider")

class TestOpenAIProvider:
    """Test OpenAI provider functionality."""
    
    @pytest.mark.asyncio
    async def test_complete_text(self, mock_settings):
        """Test text completion."""
        provider = OpenAIProvider(api_key="test_key")
        
        with patch('openai.AsyncOpenAI') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            
            mock_client.return_value.chat.completions.create.return_value = mock_response
            
            result = await provider.complete_text(
                prompt="Test prompt",
                model="gpt-4o-mini",
                max_tokens=100,
                temperature=0.7
            )
            
            assert result == "Test response"
    
    @pytest.mark.asyncio
    async def test_embed_text(self, mock_settings):
        """Test text embedding."""
        provider = OpenAIProvider(api_key="test_key")
        
        with patch('openai.AsyncOpenAI') as mock_client:
            mock_response = Mock()
            mock_response.data = [Mock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3]
            
            mock_client.return_value.embeddings.create.return_value = mock_response
            
            result = await provider.embed_text(
                text="Test text",
                model="text-embedding-ada-002"
            )
            
            assert result == [0.1, 0.2, 0.3]

class TestMistralProvider:
    """Test Mistral provider functionality."""
    
    @pytest.mark.asyncio
    async def test_complete_text(self, mock_settings):
        """Test text completion."""
        provider = MistralProvider(api_key="test_key")
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Test response"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
            mock_post.return_value = mock_response
            
            result = await provider.complete_text(
                prompt="Test prompt",
                model="mistral-small-latest",
                max_tokens=100,
                temperature=0.7
            )
            
            assert result == "Test response"

class TestAnthropicProvider:
    """Test Anthropic provider functionality."""
    
    @pytest.mark.asyncio
    async def test_complete_text(self, mock_settings):
        """Test text completion."""
        provider = AnthropicProvider(api_key="test_key")
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "content": [{"text": "Test response"}],
                "usage": {"input_tokens": 10, "output_tokens": 5}
            }
            mock_post.return_value = mock_response
            
            result = await provider.complete_text(
                prompt="Test prompt",
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.7
            )
            
            assert result == "Test response"

class TestCohereProvider:
    """Test Cohere provider functionality."""
    
    @pytest.mark.asyncio
    async def test_complete_text(self, mock_settings):
        """Test text completion."""
        provider = CohereProvider(api_key="test_key")
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "generations": [{"text": "Test response"}],
                "meta": {"billed_units": {"input_tokens": 10, "output_tokens": 5}}
            }
            mock_post.return_value = mock_response
            
            result = await provider.complete_text(
                prompt="Test prompt",
                model="command",
                max_tokens=100,
                temperature=0.7
            )
            
            assert result == "Test response"
    
    @pytest.mark.asyncio
    async def test_embed_text(self, mock_settings):
        """Test text embedding."""
        provider = CohereProvider(api_key="test_key")
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "embeddings": [[0.1, 0.2, 0.3]]
            }
            mock_post.return_value = mock_response
            
            result = await provider.embed_text(
                text="Test text",
                model="embed-english-v3.0"
            )
            
            assert result == [0.1, 0.2, 0.3]

class TestProviderHealthChecks:
    """Test provider health checks."""
    
    @pytest.mark.asyncio
    async def test_openai_health_check(self, mock_settings):
        """Test OpenAI health check."""
        provider = OpenAIProvider(api_key="test_key")
        
        with patch('openai.AsyncOpenAI') as mock_client:
            mock_client.return_value.models.list.return_value = Mock()
            
            result = await provider.health_check()
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_mistral_health_check(self, mock_settings):
        """Test Mistral health check."""
        provider = MistralProvider(api_key="test_key")
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": [{"id": "mistral-small"}]}
            mock_get.return_value = mock_response
            
            result = await provider.health_check()
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_anthropic_health_check(self, mock_settings):
        """Test Anthropic health check."""
        provider = AnthropicProvider(api_key="test_key")
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": [{"id": "claude-3"}]}
            mock_get.return_value = mock_response
            
            result = await provider.health_check()
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_cohere_health_check(self, mock_settings):
        """Test Cohere health check."""
        provider = CohereProvider(api_key="test_key")
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": [{"id": "command"}]}
            mock_get.return_value = mock_response
            
            result = await provider.health_check()
            assert result["status"] == "healthy"

class TestLLMProviders:
    """Test LLM providers."""
    
    def test_dummy(self):
        """Dummy test to ensure the test class is loaded."""
        assert True 