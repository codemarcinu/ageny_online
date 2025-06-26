import pytest
import os
import sys
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.config import Settings, get_provider_config, is_provider_available, get_available_providers, get_provider_priorities

@pytest.fixture(autouse=True)
def clear_environment(monkeypatch):
    """Clear environment variables before each test."""
    # Clear all relevant environment variables
    env_vars_to_clear = [
        "OPENAI_API_KEY", "MISTRAL_API_KEY", "AZURE_VISION_KEY", "AZURE_VISION_ENDPOINT",
        "GOOGLE_VISION_PROJECT_ID", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT",
        "WEAVIATE_URL", "WEAVIATE_API_KEY", "WEAVIATE_USERNAME", "WEAVIATE_PASSWORD"
    ]
    
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)
    
    yield

class TestSettings:
    """Test cases for application settings."""
    
    def test_settings_default_values(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.api_title == "Ageny Online API"
        assert settings.api_version == "1.0.0"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.debug == False
        assert settings.log_level == "INFO"
        assert settings.enable_metrics == True
        assert settings.enable_cost_tracking == True
    
    def test_settings_model_defaults(self):
        """Test default model settings."""
        settings = Settings()
        assert settings.openai_model == "gpt-4o-mini"
        assert settings.mistral_model == "mistral-small-latest"
        assert settings.openai_max_tokens == 1000
        assert settings.mistral_max_tokens == 1000
        assert settings.openai_temperature == 0.7
        assert settings.mistral_temperature == 0.7
    
    def test_settings_file_upload_defaults(self):
        """Test file upload settings."""
        settings = Settings()
        assert settings.max_file_size == 10 * 1024 * 1024  # 10MB
        assert "image/jpeg" in settings.allowed_image_types
        assert "image/png" in settings.allowed_image_types
        assert settings.max_batch_size == 10
        assert settings.batch_timeout == 300
    
    def test_settings_provider_priorities(self):
        """Test provider priority settings."""
        settings = Settings()
        assert settings.llm_provider_priority == ["openai", "mistral"]
        assert settings.ocr_provider_priority == ["azure_vision", "google_vision"]
        assert settings.vector_store_priority == ["pinecone", "weaviate"]
    
    def test_settings_with_environment_variables(self, monkeypatch):
        """Test settings with environment variables."""
        # Set environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-key")
        monkeypatch.setenv("AZURE_VISION_KEY", "test-azure-key")
        monkeypatch.setenv("AZURE_VISION_ENDPOINT", "https://test.cognitiveservices.azure.com/")
        monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
        monkeypatch.setenv("PINECONE_ENVIRONMENT", "test-env")
        
        # Reload settings to pick up environment variables
        test_settings = Settings()
        
        assert test_settings.openai_api_key == "test-openai-key"
        assert test_settings.mistral_api_key == "test-mistral-key"
        assert test_settings.azure_vision_key == "test-azure-key"
        assert test_settings.azure_vision_endpoint == "https://test.cognitiveservices.azure.com/"
        assert test_settings.pinecone_api_key == "test-pinecone-key"
        assert test_settings.pinecone_environment == "test-env"

class TestProviderConfig:
    """Test cases for provider configuration functions."""
    
    def test_get_provider_config_openai(self):
        """Test OpenAI provider configuration."""
        config = get_provider_config("openai")
        
        assert "api_key" in config
        assert "model" in config
        assert "max_tokens" in config
        assert "temperature" in config
        assert config["model"] == "gpt-4o-mini"
        assert config["max_tokens"] == 1000
        assert config["temperature"] == 0.7
    
    def test_get_provider_config_mistral(self):
        """Test Mistral provider configuration."""
        config = get_provider_config("mistral")
        
        assert "api_key" in config
        assert "model" in config
        assert "max_tokens" in config
        assert "temperature" in config
        assert config["model"] == "mistral-small-latest"
        assert config["max_tokens"] == 1000
        assert config["temperature"] == 0.7
    
    def test_get_provider_config_azure_vision(self):
        """Test Azure Vision provider configuration."""
        config = get_provider_config("azure_vision")
        
        assert "key" in config
        assert "endpoint" in config
        assert "region" in config
    
    def test_get_provider_config_google_vision(self):
        """Test Google Vision provider configuration."""
        config = get_provider_config("google_vision")
        
        assert "project_id" in config
        assert "credentials_path" in config
    
    def test_get_provider_config_pinecone(self):
        """Test Pinecone provider configuration."""
        config = get_provider_config("pinecone")
        
        assert "api_key" in config
        assert "environment" in config
        assert config["environment"] == "gcp-starter"
    
    def test_get_provider_config_weaviate(self):
        """Test Weaviate provider configuration."""
        config = get_provider_config("weaviate")
        
        assert "url" in config
        assert "api_key" in config
        assert "username" in config
        assert "password" in config
    
    def test_get_provider_config_invalid(self):
        """Test getting configuration for invalid provider."""
        config = get_provider_config("invalid_provider")
        
        assert config == {}

class TestProviderAvailability:
    """Test cases for provider availability functions."""
    
    def test_is_provider_available_openai_with_key(self, monkeypatch):
        """Test OpenAI availability with API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        assert is_provider_available("openai") == True
    
    def test_is_provider_available_openai_without_key(self, monkeypatch):
        """Test OpenAI availability without API key."""
        class NoEnvSettings(Settings):
            class Config:
                env_file = None
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        s = NoEnvSettings()
        assert s.openai_api_key is None
        assert is_provider_available("openai", settings=s) == False
    
    def test_is_provider_available_mistral_with_key(self, monkeypatch):
        """Test Mistral availability with API key."""
        monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-key")
        assert is_provider_available("mistral") == True
    
    def test_is_provider_available_azure_vision_with_config(self, monkeypatch):
        """Test Azure Vision availability with configuration."""
        # Create a custom settings instance to avoid caching issues
        class TestSettings(Settings):
            class Config:
                env_file = None
        
        # Set environment variables
        monkeypatch.setenv("AZURE_VISION_KEY", "test-azure-key")
        monkeypatch.setenv("AZURE_VISION_ENDPOINT", "https://test.cognitiveservices.azure.com/")
        
        # Create settings instance with the environment variables
        test_settings = TestSettings()
        assert test_settings.azure_vision_key == "test-azure-key"
        assert test_settings.azure_vision_endpoint == "https://test.cognitiveservices.azure.com/"
        
        assert is_provider_available("azure_vision", settings=test_settings) == True
    
    def test_is_provider_available_azure_vision_missing_endpoint(self, monkeypatch):
        """Test Azure Vision availability without endpoint."""
        monkeypatch.setenv("AZURE_VISION_KEY", "test-azure-key")
        # Missing endpoint
        assert is_provider_available("azure_vision") == False
    
    def test_is_provider_available_google_vision_with_project_id(self, monkeypatch):
        """Test Google Vision availability with project ID."""
        # Create a custom settings instance to avoid caching issues
        class TestSettings(Settings):
            class Config:
                env_file = None
        
        # Set environment variables
        monkeypatch.setenv("GOOGLE_VISION_PROJECT_ID", "test-project-id")
        monkeypatch.setenv("GOOGLE_VISION_CREDENTIALS_PATH", "/path/to/credentials.json")
        
        # Create settings instance with the environment variables
        test_settings = TestSettings()
        assert test_settings.google_vision_project_id == "test-project-id"
        assert test_settings.google_vision_credentials_path == "/path/to/credentials.json"
        
        # Google Vision needs both project_id and credentials_path to be considered available
        assert is_provider_available("google_vision", settings=test_settings) == True
    
    def test_is_provider_available_pinecone_with_key(self, monkeypatch):
        """Test Pinecone availability with API key."""
        # Create a custom settings instance to avoid caching issues
        class TestSettings(Settings):
            class Config:
                env_file = None
        
        # Set environment variables
        monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
        
        # Create settings instance with the environment variables
        test_settings = TestSettings()
        assert test_settings.pinecone_api_key == "test-pinecone-key"
        
        assert is_provider_available("pinecone", settings=test_settings) == True
    
    def test_is_provider_available_weaviate_with_url(self, monkeypatch):
        """Test Weaviate availability with URL."""
        # Create a custom settings instance to avoid caching issues
        class TestSettings(Settings):
            class Config:
                env_file = None
        
        # Set environment variables
        monkeypatch.setenv("WEAVIATE_URL", "https://test.weaviate.network")
        
        # Create settings instance with the environment variables
        test_settings = TestSettings()
        assert test_settings.weaviate_url == "https://test.weaviate.network"
        
        assert is_provider_available("weaviate", settings=test_settings) == True
    
    def test_is_provider_available_invalid(self):
        """Test availability for invalid provider."""
        assert is_provider_available("invalid_provider") == False

class TestProviderFunctions:
    """Test cases for provider utility functions."""
    
    def test_get_available_providers_all_configured(self, monkeypatch):
        """Test getting all available providers when all are configured."""
        # Create a custom settings instance to avoid caching issues
        class TestSettings(Settings):
            class Config:
                env_file = None
        
        # Set environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-key")
        monkeypatch.setenv("AZURE_VISION_KEY", "test-azure-key")
        monkeypatch.setenv("AZURE_VISION_ENDPOINT", "https://test.cognitiveservices.azure.com/")
        monkeypatch.setenv("GOOGLE_VISION_PROJECT_ID", "test-project-id")
        monkeypatch.setenv("GOOGLE_VISION_CREDENTIALS_PATH", "/path/to/credentials.json")
        monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
        monkeypatch.setenv("WEAVIATE_URL", "https://test.weaviate.network")
        
        # Create settings instance with the environment variables
        test_settings = TestSettings()
        
        providers = get_available_providers(settings=test_settings)
        
        assert providers["openai"] == True
        assert providers["mistral"] == True
        assert providers["azure_vision"] == True
        assert providers["google_vision"] == True
        assert providers["pinecone"] == True
        assert providers["weaviate"] == True
    
    def test_get_available_providers_none_configured(self, monkeypatch):
        """Test getting available providers when none are configured."""
        class NoEnvSettings(Settings):
            class Config:
                env_file = None
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
        monkeypatch.delenv("AZURE_VISION_KEY", raising=False)
        monkeypatch.delenv("AZURE_VISION_ENDPOINT", raising=False)
        monkeypatch.delenv("GOOGLE_VISION_PROJECT_ID", raising=False)
        monkeypatch.delenv("PINECONE_API_KEY", raising=False)
        monkeypatch.delenv("WEAVIATE_URL", raising=False)
        s = NoEnvSettings()
        assert s.openai_api_key is None
        providers = get_available_providers(settings=s)
        assert providers["openai"] == False
        assert providers["mistral"] == False
        assert providers["azure_vision"] == False
        assert providers["google_vision"] == False
        assert providers["pinecone"] == False
        assert providers["weaviate"] == False
    
    def test_get_provider_priorities(self):
        """Test getting provider priorities."""
        priorities = get_provider_priorities()
        
        assert "llm" in priorities
        assert "ocr" in priorities
        assert "vector_store" in priorities
        assert priorities["llm"] == ["openai", "mistral"]
        assert priorities["ocr"] == ["azure_vision", "google_vision"]
        assert priorities["vector_store"] == ["pinecone", "weaviate"]

class TestEnvironmentValidation:
    """Test cases for environment validation."""
    
    def test_required_environment_variables(self):
        """Test that required environment variables are defined."""
        # These should be defined in the settings class
        settings = Settings()
        assert hasattr(settings, 'openai_api_key')
        assert hasattr(settings, 'mistral_api_key')
        assert hasattr(settings, 'azure_vision_key')
        assert hasattr(settings, 'azure_vision_endpoint')
        assert hasattr(settings, 'google_vision_project_id')
        assert hasattr(settings, 'pinecone_api_key')
        assert hasattr(settings, 'weaviate_url')
    
    def test_optional_environment_variables(self):
        """Test that optional environment variables are defined."""
        settings = Settings()
        assert hasattr(settings, 'openai_organization')
        assert hasattr(settings, 'azure_vision_region')
        assert hasattr(settings, 'google_vision_credentials_path')
        assert hasattr(settings, 'pinecone_environment')
        assert hasattr(settings, 'weaviate_api_key')
        assert hasattr(settings, 'weaviate_username')
        assert hasattr(settings, 'weaviate_password')
    
    def test_server_configuration(self):
        """Test server configuration settings."""
        settings = Settings()
        assert hasattr(settings, 'host')
        assert hasattr(settings, 'port')
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'cors_origins')
        assert hasattr(settings, 'cors_credentials')
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        settings = Settings()
        assert hasattr(settings, 'rate_limit_default')
        assert hasattr(settings, 'rate_limit_strict')
        assert settings.rate_limit_default == "100/minute"
        assert settings.rate_limit_strict == "10/minute"
    
    def test_monitoring_configuration(self):
        """Test monitoring configuration."""
        settings = Settings()
        assert hasattr(settings, 'enable_metrics')
        assert hasattr(settings, 'metrics_port')
        assert hasattr(settings, 'log_level')
        assert hasattr(settings, 'log_format')
    
    def test_cost_tracking_configuration(self):
        """Test cost tracking configuration."""
        settings = Settings()
        assert hasattr(settings, 'enable_cost_tracking')
        assert settings.enable_cost_tracking == True 