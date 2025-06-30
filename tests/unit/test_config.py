"""
Unit tests for configuration management.
"""

import pytest
import os
import sys
from unittest.mock import patch, Mock
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.config import settings

@pytest.fixture(autouse=True)
def clear_environment(monkeypatch):
    """Clear environment variables before each test."""
    # Clear all relevant environment variables
    env_vars_to_clear = [
        "OPENAI_API_KEY", "MISTRAL_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY",
        "AZURE_VISION_KEY", "AZURE_VISION_ENDPOINT",
        "GOOGLE_VISION_PROJECT_ID", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT",
        "WEAVIATE_URL", "WEAVIATE_API_KEY", "WEAVIATE_USERNAME", "WEAVIATE_PASSWORD"
    ]
    
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)
    
    yield

class TestSettings:
    """Test settings configuration."""
    
    def test_settings_initialization(self):
        """Test that settings are properly initialized."""
        assert hasattr(settings, 'OPENAI_API_KEY')
        assert hasattr(settings, 'MISTRAL_API_KEY')
        assert hasattr(settings, 'ANTHROPIC_API_KEY')
        assert hasattr(settings, 'COHERE_API_KEY')
        assert hasattr(settings, 'PINECONE_API_KEY')
        assert hasattr(settings, 'WEAVIATE_URL')
    
    def test_settings_types(self):
        """Test that settings have correct types."""
        # API keys should be strings
        assert isinstance(settings.OPENAI_API_KEY, str)
        assert isinstance(settings.MISTRAL_API_KEY, str)
        assert isinstance(settings.ANTHROPIC_API_KEY, str)
        assert isinstance(settings.COHERE_API_KEY, str)
        assert isinstance(settings.PINECONE_API_KEY, str)
        
        # URLs should be strings
        assert isinstance(settings.WEAVIATE_URL, str)
        
        # Ports should be integers
        assert isinstance(settings.PORT, int)
        assert isinstance(settings.RATE_LIMIT_CHAT, int)
    
    def test_settings_defaults(self):
        """Test that settings have reasonable defaults."""
        # API keys should be empty strings by default (for security)
        assert settings.OPENAI_API_KEY == ""
        assert settings.MISTRAL_API_KEY == ""
        assert settings.ANTHROPIC_API_KEY == ""
        assert settings.COHERE_API_KEY == ""
        assert settings.PINECONE_API_KEY == ""
        
        # URLs should have default values
        assert settings.WEAVIATE_URL == "http://localhost:8080"
        assert settings.PORT == 8000
        assert settings.HOST == "0.0.0.0"

class TestEnvironmentConfiguration:
    """Test environment-specific configuration."""
    
    @patch.dict('os.environ', {
        'OPENAI_API_KEY': 'env_openai_key',
        'MISTRAL_API_KEY': 'env_mistral_key',
        'ANTHROPIC_API_KEY': 'env_anthropic_key',
        'COHERE_API_KEY': 'env_cohere_key',
        'PINECONE_API_KEY': 'env_pinecone_key',
        'WEAVIATE_URL': 'http://env-weaviate:8080'
    })
    def test_environment_variables_override(self):
        """Test that environment variables override defaults."""
        # Reload settings to pick up environment variables
        from backend.config import Settings
        test_settings = Settings()
        
        assert test_settings.OPENAI_API_KEY == "env_openai_key"
        assert test_settings.MISTRAL_API_KEY == "env_mistral_key"
        assert test_settings.ANTHROPIC_API_KEY == "env_anthropic_key"
        assert test_settings.COHERE_API_KEY == "env_cohere_key"
        assert test_settings.PINECONE_API_KEY == "env_pinecone_key"
        assert test_settings.WEAVIATE_URL == "http://env-weaviate:8080"

class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_validate_required_settings(self):
        """Test validation of required settings."""
        # Test with valid settings
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'APP_VERSION')
        assert hasattr(settings, 'ENVIRONMENT')
    
    def test_validate_missing_api_keys(self):
        """Test validation with missing API keys."""
        # Test with missing API keys (should not raise exceptions)
        assert settings.OPENAI_API_KEY == ""
        assert settings.MISTRAL_API_KEY == ""
        assert settings.ANTHROPIC_API_KEY == ""
        assert settings.COHERE_API_KEY == ""

class TestConfigurationHelpers:
    """Test configuration helper methods."""
    
    def test_is_provider_configured(self):
        """Test checking if provider is configured."""
        # Test with configured provider (should use actual settings)
        assert hasattr(settings, 'is_openai_configured')
        assert hasattr(settings, 'is_mistral_configured')
        assert hasattr(settings, 'is_anthropic_configured')
        assert hasattr(settings, 'is_cohere_configured')
    
    def test_get_configured_providers(self):
        """Test getting configured providers."""
        # Test that we can access provider configuration methods
        assert hasattr(settings, 'get_available_providers')
        assert callable(settings.get_available_providers)

class TestProviderAvailability:
    """Test provider availability checks."""
    
    def test_is_provider_available_openai_with_key(self, monkeypatch):
        """Test OpenAI availability with API key."""
        monkeypatch.setenv('OPENAI_API_KEY', 'test_key')
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_openai_configured() == True
    
    def test_is_provider_available_openai_without_key(self, monkeypatch):
        """Test OpenAI availability without API key."""
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_openai_configured() == False
    
    def test_is_provider_available_mistral_with_key(self, monkeypatch):
        """Test Mistral availability with API key."""
        monkeypatch.setenv('MISTRAL_API_KEY', 'test_key')
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_mistral_configured() == True
    
    def test_is_provider_available_azure_vision_with_config(self, monkeypatch):
        """Test Azure Vision availability with configuration."""
        monkeypatch.setenv('AZURE_VISION_KEY', 'test_key')
        monkeypatch.setenv('AZURE_VISION_ENDPOINT', 'test_endpoint')
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_azure_vision_configured() == True
    
    def test_is_provider_available_azure_vision_missing_endpoint(self, monkeypatch):
        """Test Azure Vision availability without endpoint."""
        monkeypatch.setenv('AZURE_VISION_KEY', 'test_key')
        monkeypatch.delenv('AZURE_VISION_ENDPOINT', raising=False)
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_azure_vision_configured() == False
    
    def test_is_provider_available_google_vision_with_project_id(self, monkeypatch):
        """Test Google Vision availability with project ID."""
        monkeypatch.setenv('GOOGLE_VISION_PROJECT_ID', 'test_project')
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_google_vision_configured() == True
    
    def test_is_provider_available_pinecone_with_key(self, monkeypatch):
        """Test Pinecone availability with API key."""
        monkeypatch.setenv('PINECONE_API_KEY', 'test_key')
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_pinecone_configured() == True
    
    def test_is_provider_available_weaviate_with_url(self, monkeypatch):
        """Test Weaviate availability with URL."""
        monkeypatch.setenv('WEAVIATE_URL', 'http://test-weaviate:8080')
        from backend.config import Settings
        test_settings = Settings()
        assert test_settings.is_weaviate_configured() == True
    
    def test_is_provider_available_invalid(self):
        """Test availability check for invalid provider."""
        # Test that invalid provider methods don't exist
        assert not hasattr(settings, 'is_invalid_provider_configured')

class TestProviderFunctions:
    """Test provider-related functions."""
    
    def test_get_available_providers_all_configured(self, monkeypatch):
        """Test getting available providers when all are configured."""
        monkeypatch.setenv('OPENAI_API_KEY', 'test_key')
        monkeypatch.setenv('MISTRAL_API_KEY', 'test_key')
        monkeypatch.setenv('ANTHROPIC_API_KEY', 'test_key')
        monkeypatch.setenv('COHERE_API_KEY', 'test_key')
        
        from backend.config import Settings
        test_settings = Settings()
        providers = test_settings.get_available_providers()
        
        assert isinstance(providers, dict)
        assert 'openai' in providers
        assert 'mistral' in providers
        assert 'anthropic' in providers
        assert 'cohere' in providers
    
    def test_get_available_providers_none_configured(self, monkeypatch):
        """Test getting available providers when none are configured."""
        # Clear all API keys
        env_vars_to_clear = [
            "OPENAI_API_KEY", "MISTRAL_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY"
        ]
        for var in env_vars_to_clear:
            monkeypatch.delenv(var, raising=False)
        
        from backend.config import Settings
        test_settings = Settings()
        providers = test_settings.get_available_providers()
        
        assert isinstance(providers, dict)
        # All should be False when no keys are set
        for provider, configured in providers.items():
            assert configured == False
    
    def test_get_provider_priorities(self):
        """Test getting provider priorities."""
        priorities = {
            'openai': settings.PROVIDER_PRIORITY_OPENAI,
            'anthropic': settings.PROVIDER_PRIORITY_ANTHROPIC,
            'cohere': settings.PROVIDER_PRIORITY_COHERE,
            'mistral': settings.PROVIDER_PRIORITY_MISTRAL,
        }
        
        assert priorities['openai'] == 1
        assert priorities['anthropic'] == 2
        assert priorities['cohere'] == 3
        assert priorities['mistral'] == 4

class TestEnvironmentValidation:
    """Test environment validation."""
    
    def test_required_environment_variables(self):
        """Test required environment variables."""
        # Test that basic settings are available
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'APP_VERSION')
        assert hasattr(settings, 'ENVIRONMENT')
    
    def test_optional_environment_variables(self):
        """Test optional environment variables."""
        # Test that optional settings have defaults
        assert hasattr(settings, 'DEBUG')
        assert hasattr(settings, 'LOG_LEVEL')
        assert hasattr(settings, 'PORT')
        assert hasattr(settings, 'HOST')
    
    def test_server_configuration(self):
        """Test server configuration."""
        # Test server-related settings
        assert hasattr(settings, 'HOST')
        assert hasattr(settings, 'PORT')
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        # Test rate limiting settings
        assert hasattr(settings, 'RATE_LIMIT_ENABLED')
        assert hasattr(settings, 'RATE_LIMIT_CHAT')
        assert hasattr(settings, 'RATE_LIMIT_UPLOAD')
        assert hasattr(settings, 'RATE_LIMIT_RAG')
        assert settings.RATE_LIMIT_ENABLED == True
    
    def test_monitoring_configuration(self):
        """Test monitoring configuration."""
        # Test monitoring settings
        assert hasattr(settings, 'PROMETHEUS_ENABLED')
        assert hasattr(settings, 'ENABLE_METRICS')
        assert settings.PROMETHEUS_ENABLED == True
        assert settings.ENABLE_METRICS == True
    
    def test_cost_tracking_configuration(self):
        """Test cost tracking configuration."""
        # Test cost tracking settings
        assert hasattr(settings, 'COST_TRACKING_ENABLED')
        assert hasattr(settings, 'MONTHLY_BUDGET')
        assert hasattr(settings, 'COST_ALERT_THRESHOLD')
        assert settings.COST_TRACKING_ENABLED == True 