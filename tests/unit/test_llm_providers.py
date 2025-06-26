import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.core.llm_providers.openai_client import OpenAIProvider, ModelConfig
from backend.core.llm_providers.mistral_client import MistralProvider
from backend.core.llm_providers.provider_factory import LLMProviderFactory, ProviderType, ProviderConfig

class TestOpenAIProvider:
    """Test cases for OpenAI provider."""
    
    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        provider = OpenAIProvider("test-api-key")
        
        assert provider.default_model == "gpt-4o-mini"
        assert "gpt-4o-mini" in provider.models
        assert "gpt-4o" in provider.models
        assert "gpt-3.5-turbo" in provider.models
    
    def test_openai_provider_initialization_without_key(self):
        """Test OpenAI provider initialization without API key."""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            OpenAIProvider("")
    
    def test_openai_model_config(self):
        """Test OpenAI model configuration."""
        provider = OpenAIProvider("test-api-key")
        
        gpt4_config = provider.get_model_config("gpt-4o")
        assert gpt4_config.max_tokens == 128000
        assert gpt4_config.cost_per_1k_input == 0.005
        assert gpt4_config.cost_per_1k_output == 0.015
    
    def test_openai_get_available_models(self):
        """Test getting available models."""
        provider = OpenAIProvider("test-api-key")
        models = provider.get_available_models()
        
        assert "gpt-4o" in models
        assert "gpt-4o-mini" in models
        assert "gpt-3.5-turbo" in models
    
    @pytest.mark.asyncio
    async def test_openai_chat_completion(self, mock_openai_response):
        """Test OpenAI chat completion."""
        with patch('backend.core.llm_providers.openai_client.AsyncOpenAI') as mock_client:
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = mock_openai_response["text"]
            mock_response.choices[0].finish_reason = mock_openai_response["finish_reason"]
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = mock_openai_response["usage"]["prompt_tokens"]
            mock_response.usage.completion_tokens = mock_openai_response["usage"]["completion_tokens"]
            mock_response.usage.total_tokens = mock_openai_response["usage"]["total_tokens"]
            
            # Make the mock async
            mock_client.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
            
            provider = OpenAIProvider("test-api-key")
            messages = [{"role": "user", "content": "Hello"}]
            
            result = await provider.chat(messages)
            
            assert result["text"] == mock_openai_response["text"]
            assert result["model"] == "gpt-4o-mini"
            assert result["usage"]["total_tokens"] == mock_openai_response["usage"]["total_tokens"]
            assert "cost" in result
    
    @pytest.mark.asyncio
    async def test_openai_embedding(self):
        """Test OpenAI embedding generation."""
        with patch('backend.core.llm_providers.openai_client.AsyncOpenAI') as mock_client:
            # Setup mock response
            mock_response = Mock()
            mock_response.data = [Mock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3]
            mock_response.usage = Mock()
            mock_response.usage.total_tokens = 10
            
            # Make the mock async
            mock_client.return_value.embeddings.create = AsyncMock(return_value=mock_response)
            
            provider = OpenAIProvider("test-api-key")
            texts = ["Hello world"]
            
            result = await provider.embed(texts)
            
            assert "embeddings" in result
            assert len(result["embeddings"]) == 1
            assert result["embeddings"][0] == [0.1, 0.2, 0.3]
            assert "cost" in result

class TestMistralProvider:
    """Test cases for Mistral provider."""
    
    def test_mistral_provider_initialization(self):
        """Test Mistral provider initialization."""
        provider = MistralProvider("test-api-key")
        
        assert provider.default_model == "mistral-small-latest"
        assert "mistral-small-latest" in provider.models
        assert "mistral-large-latest" in provider.models
    
    def test_mistral_provider_initialization_without_key(self):
        """Test Mistral provider initialization without API key."""
        with pytest.raises(ValueError, match="Mistral API key is required"):
            MistralProvider("")
    
    def test_mistral_get_available_models(self):
        """Test getting available models."""
        provider = MistralProvider("test-api-key")
        models = provider.get_available_models()
        
        assert "mistral-small-latest" in models
        assert "mistral-large-latest" in models
        assert "mistral-medium-latest" in models
    
    @pytest.mark.asyncio
    async def test_mistral_chat_completion(self, mock_mistral_response):
        """Test Mistral chat completion."""
        with patch('backend.core.llm_providers.mistral_client.asyncio.to_thread') as mock_to_thread:
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = mock_mistral_response["text"]
            mock_response.choices[0].finish_reason = mock_mistral_response["finish_reason"]
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = mock_mistral_response["usage"]["prompt_tokens"]
            mock_response.usage.completion_tokens = mock_mistral_response["usage"]["completion_tokens"]
            mock_response.usage.total_tokens = mock_mistral_response["usage"]["total_tokens"]
            
            # Mock the to_thread call to return the response directly
            mock_to_thread.return_value = mock_response
            
            provider = MistralProvider("test-api-key")
            messages = [{"role": "user", "content": "Hello"}]
            
            result = await provider.chat(messages)
            
            assert result["text"] == mock_mistral_response["text"]
            assert result["model"] == "mistral-small-latest"
            assert result["usage"]["total_tokens"] == mock_mistral_response["usage"]["total_tokens"]
            assert "cost" in result

class TestLLMProviderFactory:
    """Test cases for LLM provider factory."""
    
    def test_factory_initialization(self):
        """Test factory initialization."""
        factory = LLMProviderFactory()
        
        assert ProviderType.OPENAI in factory._providers
        assert ProviderType.MISTRAL in factory._providers
    
    def test_register_provider(self):
        """Test provider registration."""
        factory = LLMProviderFactory()
        
        config = ProviderConfig(
            api_key="test-key",
            priority=1
        )
        
        factory.register_provider(ProviderType.OPENAI, config)
        
        assert ProviderType.OPENAI in factory._configs
        assert factory._configs[ProviderType.OPENAI] == config
    
    def test_register_invalid_provider(self):
        """Test registering invalid provider type."""
        factory = LLMProviderFactory()
        
        config = ProviderConfig(api_key="test-key")
        
        with pytest.raises(ValueError, match="Unsupported provider type"):
            factory.register_provider("invalid", config)
    
    def test_get_provider_not_configured(self):
        """Test getting provider that is not configured."""
        factory = LLMProviderFactory()
        
        with pytest.raises(ValueError, match="Provider openai not configured"):
            factory.get_provider(ProviderType.OPENAI)
    
    @pytest.mark.asyncio
    async def test_chat_with_fallback(self, sample_messages):
        """Test chat with fallback mechanism."""
        factory = LLMProviderFactory()
        
        # Register providers
        factory.register_provider(
            ProviderType.OPENAI,
            ProviderConfig(api_key="test-key", priority=1)
        )
        factory.register_provider(
            ProviderType.MISTRAL,
            ProviderConfig(api_key="test-key", priority=2)
        )
        
        with patch.object(factory, 'get_provider') as mock_get_provider:
            # Mock provider that succeeds
            mock_provider = Mock()
            mock_provider.chat = AsyncMock(return_value={
                "text": "Success response",
                "model": "test-model",
                "usage": {"total_tokens": 10},
                "cost": {"total_cost": 0.01}
            })
            mock_get_provider.return_value = mock_provider
            
            result = await factory.chat_with_fallback(sample_messages)
            
            assert result["text"] == "Success response"
            assert result["provider"] == "openai"
    
    @pytest.mark.asyncio
    async def test_chat_with_fallback_all_fail(self, sample_messages):
        """Test chat with fallback when all providers fail."""
        factory = LLMProviderFactory()
        
        # Register providers
        factory.register_provider(
            ProviderType.OPENAI,
            ProviderConfig(api_key="test-key", priority=1)
        )
        factory.register_provider(
            ProviderType.MISTRAL,
            ProviderConfig(api_key="test-key", priority=2)
        )
        
        with patch.object(factory, 'get_provider') as mock_get_provider:
            # Mock provider that fails
            mock_provider = Mock()
            mock_provider.chat = AsyncMock(side_effect=Exception("API Error"))
            mock_get_provider.return_value = mock_provider
            
            with pytest.raises(RuntimeError, match="All providers failed"):
                await factory.chat_with_fallback(sample_messages)
    
    def test_adapt_model_for_provider(self):
        """Test model adaptation for different providers."""
        factory = LLMProviderFactory()
        
        # Test OpenAI model mapping
        result = factory._adapt_model_for_provider("gpt-4", ProviderType.OPENAI)
        assert result == "gpt-4o"
        
        # Test Mistral model mapping
        result = factory._adapt_model_for_provider("gpt-4", ProviderType.MISTRAL)
        assert result == "mistral-large-latest"
        
        # Test unknown model
        result = factory._adapt_model_for_provider("unknown-model", ProviderType.OPENAI)
        assert result == "unknown-model"
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        factory = LLMProviderFactory()
        
        # No providers registered
        assert factory.get_available_providers() == []
        
        # Register providers
        factory.register_provider(
            ProviderType.OPENAI,
            ProviderConfig(api_key="test-key", priority=1)
        )
        factory.register_provider(
            ProviderType.MISTRAL,
            ProviderConfig(api_key="test-key", priority=2)
        )
        
        providers = factory.get_available_providers()
        assert "openai" in providers
        assert "mistral" in providers
        assert providers[0] == "openai"  # Higher priority first
    
    def test_get_provider_status(self):
        """Test getting provider status."""
        factory = LLMProviderFactory()
        
        status = factory.get_provider_status()
        
        assert status["openai"] == False
        assert status["mistral"] == False
        
        # Register a provider
        factory.register_provider(
            ProviderType.OPENAI,
            ProviderConfig(api_key="test-key")
        )
        
        status = factory.get_provider_status()
        assert status["openai"] == True
        assert status["mistral"] == False 