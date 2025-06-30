"""
Configuration settings for Ageny Online application.
Ustawienia są wczytywane ze zmiennych środowiskowych lub pliku .env.
"""

from __future__ import annotations

import os
import secrets
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Set User-Agent environment variable early to prevent warnings
os.environ.setdefault(
    "USER_AGENT", "Ageny-Online/1.0.0 (https://github.com/codemarcinu/ageny_online)"
)


class Settings(BaseSettings):
    """
    Główna klasa do zarządzania ustawieniami aplikacji.
    Ustawienia są wczytywane ze zmiennych środowiskowych lub pliku .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env.online",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =============================================================================
    # PODSTAWOWE USTAWIENIA APLIKACJI
    # =============================================================================

    APP_NAME: str = "Ageny Online"
    APP_VERSION: str = "1.0.0"

    # Environment configuration
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    TELEMETRY_ENABLED: bool = False

    # User Agent for HTTP requests
    USER_AGENT: str = "Ageny-Online/1.0.0 (https://github.com/codemarcinu/ageny_online)"

    # =============================================================================
    # KONFIGURACJA BAZY DANYCH
    # =============================================================================

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ageny_online.db"

    # =============================================================================
    # KONFIGURACJA REDIS
    # =============================================================================

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_USE_CACHE: bool = True

    @property
    def REDIS_URL(self) -> str:
        """Get Redis URL from configuration"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # =============================================================================
    # KONFIGURACJA OPENAI
    # =============================================================================

    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    OPENAI_ORGANIZATION: Optional[str] = Field(default=None, description="OpenAI Organization ID")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", description="OpenAI Base URL")
    
    # OpenAI Models
    OPENAI_CHAT_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI Chat Model")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", description="OpenAI Embedding Model")
    OPENAI_MAX_TOKENS: int = Field(default=1000, description="OpenAI Max Tokens")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="OpenAI Temperature")

    # =============================================================================
    # KONFIGURACJA ANTHROPIC
    # =============================================================================

    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key")
    ANTHROPIC_BASE_URL: str = Field(default="https://api.anthropic.com", description="Anthropic Base URL")
    
    # Anthropic Models
    ANTHROPIC_CHAT_MODEL: str = Field(default="claude-3-sonnet-20240229", description="Anthropic Chat Model")
    ANTHROPIC_MAX_TOKENS: int = Field(default=1000, description="Anthropic Max Tokens")
    ANTHROPIC_TEMPERATURE: float = Field(default=0.7, description="Anthropic Temperature")

    # =============================================================================
    # KONFIGURACJA COHERE
    # =============================================================================

    COHERE_API_KEY: str = Field(default="", description="Cohere API Key")
    COHERE_BASE_URL: str = Field(default="https://api.cohere.ai", description="Cohere Base URL")
    
    # Cohere Models
    COHERE_EMBEDDING_MODEL: str = Field(default="embed-english-v3.0", description="Cohere Embedding Model")
    COHERE_CHAT_MODEL: str = Field(default="command-r-plus", description="Cohere Chat Model")

    # =============================================================================
    # KONFIGURACJA MISTRAL AI
    # =============================================================================

    MISTRAL_API_KEY: str = Field(default="", description="Mistral AI API Key")
    MISTRAL_BASE_URL: str = Field(default="https://api.mistral.ai/v1", description="Mistral AI Base URL")
    
    # Mistral Models
    MISTRAL_CHAT_MODEL: str = Field(default="mistral-large-latest", description="Mistral Chat Model")
    MISTRAL_VISION_MODEL: str = Field(default="mistral-large-latest", description="Mistral Vision Model")
    MISTRAL_MAX_TOKENS: int = Field(default=4096, description="Mistral Max Tokens")
    MISTRAL_TEMPERATURE: float = Field(default=0.1, description="Mistral Temperature")

    # =============================================================================
    # KONFIGURACJA PERPLEXITY
    # =============================================================================

    PERPLEXITY_API_KEY: str = Field(default="", description="Perplexity API Key")
    PERPLEXITY_BASE_URL: str = Field(default="https://api.perplexity.ai", description="Perplexity Base URL")
    
    # Perplexity Models
    PERPLEXITY_CHAT_MODEL: str = Field(default="sonar-pro", description="Perplexity Chat Model")
    PERPLEXITY_SEARCH_MODEL: str = Field(default="sonar-pro-online", description="Perplexity Search Model")
    PERPLEXITY_MAX_TOKENS: int = Field(default=4096, description="Perplexity Max Tokens")
    PERPLEXITY_TEMPERATURE: float = Field(default=0.1, description="Perplexity Temperature")

    # =============================================================================
    # KONFIGURACJA PINECONE
    # =============================================================================

    PINECONE_API_KEY: str = Field(default="", description="Pinecone API Key")
    PINECONE_ENVIRONMENT: str = Field(default="", description="Pinecone Environment")
    PINECONE_INDEX_NAME: str = Field(default="ageny-online-index", description="Pinecone Index Name")
    PINECONE_DIMENSION: int = Field(default=1536, description="Pinecone Vector Dimension")

    # =============================================================================
    # KONFIGURACJA WEAVIATE
    # =============================================================================

    WEAVIATE_URL: str = Field(default="http://localhost:8080", description="Weaviate URL")
    WEAVIATE_API_KEY: str = Field(default="", description="Weaviate API Key")
    WEAVIATE_CLASS_NAME: str = Field(default="AgenyDocument", description="Weaviate Class Name")

    # =============================================================================
    # KONFIGURACJA AZURE VISION
    # =============================================================================

    AZURE_VISION_ENDPOINT: str = Field(default="", description="Azure Vision Endpoint")
    AZURE_VISION_KEY: str = Field(default="", description="Azure Vision Key")

    # =============================================================================
    # KONFIGURACJA GOOGLE VISION
    # =============================================================================

    GOOGLE_VISION_CREDENTIALS_PATH: str = Field(default="./config/google-credentials.json", description="Google Vision Credentials Path")
    GOOGLE_VISION_PROJECT_ID: str = Field(default="", description="Google Vision Project ID")

    # =============================================================================
    # KONFIGURACJA BEZPIECZEŃSTWA
    # =============================================================================

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="Secret Key")
    ENCRYPTION_KEY: str = Field(default="", description="Encryption Key for API Keys")
    
    # JWT Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="JWT Secret Key")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # =============================================================================
    # KONFIGURACJA MONITORINGU
    # =============================================================================

    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "./logs/backend.log"
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp"
    ENABLE_METRICS: bool = True
    PROMETHEUS_ENABLED: bool = True

    # =============================================================================
    # BACKEND - FASTAPI
    # =============================================================================

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    UVICORN_RELOAD: bool = False
    UVICORN_RELOAD_DIRS: str = "./src"
    ENABLE_DEBUG_TOOLBAR: bool = False
    ENABLE_SQL_LOGGING: bool = False

    # =============================================================================
    # CORS I BEZPIECZEŃSTWO
    # =============================================================================

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,http://frontend:3000"

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # =============================================================================
    # RAG SYSTEM
    # =============================================================================

    RAG_VECTOR_STORE_PATH: str = "./data/vector_store"
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200

    # =============================================================================
    # COST TRACKING
    # =============================================================================

    MONTHLY_BUDGET: float = 100.0
    COST_ALERT_THRESHOLD: float = 80.0
    COST_TRACKING_ENABLED: bool = True
    
    # Provider priorities (lower number = higher priority)
    PROVIDER_PRIORITY_OPENAI: int = 1
    PROVIDER_PRIORITY_ANTHROPIC: int = 2
    PROVIDER_PRIORITY_COHERE: int = 3
    PROVIDER_PRIORITY_MISTRAL: int = 4
    PROVIDER_PRIORITY_PERPLEXITY: int = 5

    # =============================================================================
    # RATE LIMITING
    # =============================================================================

    RATE_LIMIT_CHAT: int = 100
    RATE_LIMIT_UPLOAD: int = 10
    RATE_LIMIT_RAG: int = 50
    RATE_LIMIT_ENABLED: bool = True

    # =============================================================================
    # DEVELOPMENT SPECIFIC
    # =============================================================================

    LOAD_TEST_DATA: bool = False
    SEED_DATABASE: bool = False

    # =============================================================================
    # EXTERNAL SERVICES (opcjonalne)
    # =============================================================================

    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    WEATHER_API_KEY: str = Field(default="", description="Weather API Key")

    # =============================================================================
    # TELEGRAM BOT (OPCJONALNE)
    # =============================================================================

    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram Bot Token")
    TELEGRAM_WEBHOOK_URL: str = Field(default="", description="Telegram Webhook URL")
    TELEGRAM_WEBHOOK_SECRET: str = Field(default="", description="Telegram Webhook Secret")

    # =============================================================================
    # VALIDATION METHODS
    # =============================================================================

    def is_openai_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return bool(self.OPENAI_API_KEY)

    def is_anthropic_configured(self) -> bool:
        """Check if Anthropic is properly configured"""
        return bool(self.ANTHROPIC_API_KEY)

    def is_cohere_configured(self) -> bool:
        """Check if Cohere is properly configured"""
        return bool(self.COHERE_API_KEY)

    def is_pinecone_configured(self) -> bool:
        """Check if Pinecone is properly configured"""
        return bool(self.PINECONE_API_KEY and self.PINECONE_ENVIRONMENT)

    def is_weaviate_configured(self) -> bool:
        """Check if Weaviate is properly configured"""
        return bool(self.WEAVIATE_URL)

    def is_azure_vision_configured(self) -> bool:
        """Check if Azure Vision is properly configured"""
        return bool(self.AZURE_VISION_ENDPOINT and self.AZURE_VISION_KEY)

    def is_google_vision_configured(self) -> bool:
        """Check if Google Vision is properly configured"""
        return bool(self.GOOGLE_VISION_CREDENTIALS_PATH and self.GOOGLE_VISION_PROJECT_ID)

    def is_mistral_configured(self) -> bool:
        """Check if Mistral is configured."""
        return bool(self.MISTRAL_API_KEY)

    def is_perplexity_configured(self) -> bool:
        """Check if Perplexity is configured."""
        return bool(self.PERPLEXITY_API_KEY)

    def get_available_providers(self) -> dict[str, bool]:
        """Get dictionary of available providers"""
        return {
            "openai": self.is_openai_configured(),
            "anthropic": self.is_anthropic_configured(),
            "cohere": self.is_cohere_configured(),
            "mistral": self.is_mistral_configured(),
            "pinecone": self.is_pinecone_configured(),
            "weaviate": self.is_weaviate_configured(),
            "azure_vision": self.is_azure_vision_configured(),
            "google_vision": self.is_google_vision_configured(),
            "perplexity": self.is_perplexity_configured(),
        }

    # =============================================================================
    # ALIASY DLA KOMPATYBILNOŚCI Z TESTAMI
    # =============================================================================

    @property
    def openai_api_key(self) -> str:
        """Alias for OPENAI_API_KEY"""
        return self.OPENAI_API_KEY

    @property
    def mistral_api_key(self) -> str:
        """Alias for MISTRAL_API_KEY"""
        return self.MISTRAL_API_KEY

    @property
    def anthropic_api_key(self) -> str:
        """Alias for ANTHROPIC_API_KEY"""
        return self.ANTHROPIC_API_KEY

    @property
    def cohere_api_key(self) -> str:
        """Get Cohere API key."""
        return self.COHERE_API_KEY

    @property
    def pinecone_api_key(self) -> str:
        """Alias for PINECONE_API_KEY"""
        return self.PINECONE_API_KEY

    @property
    def weaviate_url(self) -> str:
        """Alias for WEAVIATE_URL"""
        return self.WEAVIATE_URL

    @property
    def weaviate_port(self) -> int:
        """Get Weaviate port from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.WEAVIATE_URL)
            return parsed.port or 8080
        except:
            return 8080

    @property
    def perplexity_api_key(self) -> str:
        """Get Perplexity API key."""
        return self.PERPLEXITY_API_KEY


# Create global settings instance
settings = Settings()
