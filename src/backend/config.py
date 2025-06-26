"""
Configuration management for Ageny Online application.

This module provides centralized configuration management using Pydantic Settings,
with support for multiple LLM, OCR, and vector store providers.
"""

import os
from enum import Enum
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env.online file
load_dotenv(".env.online")


class LogLevel(str, Enum):
    """Available log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ProviderType(str, Enum):
    """Available provider types."""
    OPENAI = "openai"
    MISTRAL = "mistral"
    AZURE_VISION = "azure_vision"
    GOOGLE_VISION = "google_vision"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"


@dataclass(frozen=True)
class LLMProviderConfig:
    """Configuration for LLM providers."""
    api_key: Optional[str]
    model: str
    max_tokens: int
    temperature: float
    organization: Optional[str] = None

    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        return bool(self.api_key and self.model)


@dataclass(frozen=True)
class OCRProviderConfig:
    """Configuration for OCR providers."""
    key: Optional[str] = None
    endpoint: Optional[str] = None
    region: Optional[str] = None
    project_id: Optional[str] = None
    credentials_path: Optional[str] = None

    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        if self.key and self.endpoint:  # Azure Vision
            return True
        if self.project_id:  # Google Vision
            return True
        return False


@dataclass(frozen=True)
class VectorStoreConfig:
    """Configuration for vector store providers."""
    api_key: Optional[str] = None
    url: Optional[str] = None
    environment: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        if self.api_key:  # Pinecone
            return True
        if self.url:  # Weaviate
            return True
        return False


class Settings(BaseSettings):
    """
    Application settings for Ageny Online.
    
    This class manages all configuration settings for the application,
    including API keys, server settings, and provider configurations.
    """
    
    # API Configuration
    api_title: str = Field(
        default="Ageny Online API",
        description="Title of the API"
    )
    api_version: str = Field(
        default="1.0.0",
        description="API version"
    )
    api_description: str = Field(
        default="Online AI Agents API with external LLM and OCR providers",
        description="API description"
    )
    
    # Server Configuration
    host: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="Server host address"
    )
    port: int = Field(
        default=8000,
        env="PORT",
        ge=1,
        le=65535,
        description="Server port number"
    )
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS",
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(
        default=True,
        env="CORS_CREDENTIALS",
        description="Allow CORS credentials"
    )
    
    # Rate Limiting
    rate_limit_default: str = Field(
        default="100/minute",
        env="RATE_LIMIT_DEFAULT",
        description="Default rate limit"
    )
    rate_limit_strict: str = Field(
        default="10/minute",
        env="RATE_LIMIT_STRICT",
        description="Strict rate limit"
    )
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        env="OPENAI_API_KEY",
        description="OpenAI API key"
    )
    openai_organization: Optional[str] = Field(
        default=None,
        env="OPENAI_ORGANIZATION",
        description="OpenAI organization ID"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        env="OPENAI_MODEL",
        description="OpenAI model to use"
    )
    openai_max_tokens: int = Field(
        default=1000,
        env="OPENAI_MAX_TOKENS",
        ge=1,
        le=8192,
        description="Maximum tokens for OpenAI"
    )
    openai_temperature: float = Field(
        default=0.7,
        env="OPENAI_TEMPERATURE",
        ge=0.0,
        le=2.0,
        description="Temperature for OpenAI"
    )
    
    # Mistral Configuration
    mistral_api_key: Optional[str] = Field(
        default=None,
        env="MISTRAL_API_KEY",
        description="Mistral API key"
    )
    mistral_model: str = Field(
        default="mistral-small-latest",
        env="MISTRAL_MODEL",
        description="Mistral model to use"
    )
    mistral_max_tokens: int = Field(
        default=1000,
        env="MISTRAL_MAX_TOKENS",
        ge=1,
        le=8192,
        description="Maximum tokens for Mistral"
    )
    mistral_temperature: float = Field(
        default=0.7,
        env="MISTRAL_TEMPERATURE",
        ge=0.0,
        le=2.0,
        description="Temperature for Mistral"
    )
    
    # Azure Vision Configuration
    azure_vision_key: Optional[str] = Field(
        default=None,
        env="AZURE_VISION_KEY",
        description="Azure Vision API key"
    )
    azure_vision_endpoint: Optional[str] = Field(
        default=None,
        env="AZURE_VISION_ENDPOINT",
        description="Azure Vision endpoint"
    )
    azure_vision_region: Optional[str] = Field(
        default=None,
        env="AZURE_VISION_REGION",
        description="Azure Vision region"
    )
    
    # Google Vision Configuration
    google_vision_project_id: Optional[str] = Field(
        default=None,
        env="GOOGLE_VISION_PROJECT_ID",
        description="Google Vision project ID"
    )
    google_vision_credentials_path: Optional[str] = Field(
        default=None,
        env="GOOGLE_VISION_CREDENTIALS_PATH",
        description="Path to Google Vision credentials file"
    )
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = Field(
        default=None,
        env="PINECONE_API_KEY",
        description="Pinecone API key"
    )
    pinecone_environment: str = Field(
        default="gcp-starter",
        env="PINECONE_ENVIRONMENT",
        description="Pinecone environment"
    )
    
    # Weaviate Configuration
    weaviate_url: Optional[str] = Field(
        default=None,
        env="WEAVIATE_URL",
        description="Weaviate server URL"
    )
    weaviate_api_key: Optional[str] = Field(
        default=None,
        env="WEAVIATE_API_KEY",
        description="Weaviate API key"
    )
    weaviate_username: Optional[str] = Field(
        default=None,
        env="WEAVIATE_USERNAME",
        description="Weaviate username"
    )
    weaviate_password: Optional[str] = Field(
        default=None,
        env="WEAVIATE_PASSWORD",
        description="Weaviate password"
    )
    
    # Database Configuration
    database_url: Optional[str] = Field(
        default=None,
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Logging Configuration
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        env="LOG_LEVEL",
        description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    
    # Monitoring Configuration
    enable_metrics: bool = Field(
        default=True,
        env="ENABLE_METRICS",
        description="Enable metrics collection"
    )
    metrics_port: int = Field(
        default=9090,
        env="METRICS_PORT",
        ge=1,
        le=65535,
        description="Metrics server port"
    )
    
    # Cost Tracking
    enable_cost_tracking: bool = Field(
        default=True,
        env="ENABLE_COST_TRACKING",
        description="Enable cost tracking"
    )
    
    # File Upload Configuration
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        env="MAX_FILE_SIZE",
        ge=1024,  # Minimum 1KB
        le=100 * 1024 * 1024,  # Maximum 100MB
        description="Maximum file size in bytes"
    )
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        description="Allowed image MIME types"
    )
    
    # Batch Processing Configuration
    max_batch_size: int = Field(
        default=10,
        env="MAX_BATCH_SIZE",
        ge=1,
        le=100,
        description="Maximum batch size"
    )
    batch_timeout: int = Field(
        default=300,  # 5 minutes
        env="BATCH_TIMEOUT",
        ge=60,  # Minimum 1 minute
        le=3600,  # Maximum 1 hour
        description="Batch processing timeout in seconds"
    )
    
    # Provider Priority Configuration
    llm_provider_priority: List[str] = Field(
        default=["openai", "mistral"],
        env="LLM_PROVIDER_PRIORITY",
        description="LLM provider priority order"
    )
    ocr_provider_priority: List[str] = Field(
        default=["azure_vision", "google_vision"],
        env="OCR_PROVIDER_PRIORITY",
        description="OCR provider priority order"
    )
    vector_store_priority: List[str] = Field(
        default=["pinecone", "weaviate"],
        env="VECTOR_STORE_PRIORITY",
        description="Vector store provider priority order"
    )

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string to list if needed."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @field_validator('llm_provider_priority', 'ocr_provider_priority', 'vector_store_priority', mode='before')
    @classmethod
    def parse_provider_priorities(cls, v):
        """Parse provider priorities from string to list if needed."""
        if isinstance(v, str):
            return [provider.strip() for provider in v.split(',')]
        return v

    @field_validator('allowed_image_types', mode='before')
    @classmethod
    def parse_allowed_image_types(cls, v):
        """Parse allowed image types from string to list if needed."""
        if isinstance(v, str):
            return [img_type.strip() for img_type in v.split(',')]
        return v

    @model_validator(mode='after')
    def validate_provider_configurations(self):
        """Validate provider configurations."""
        # Validate OpenAI configuration
        if self.openai_api_key and not self.openai_model:
            raise ValueError("OpenAI model must be specified when API key is provided")
        
        # Validate Mistral configuration
        if self.mistral_api_key and not self.mistral_model:
            raise ValueError("Mistral model must be specified when API key is provided")
        
        # Validate Azure Vision configuration
        if self.azure_vision_key and not self.azure_vision_endpoint:
            raise ValueError("Azure Vision endpoint must be specified when API key is provided")
        
        # Validate Google Vision configuration
        if self.google_vision_project_id and not self.google_vision_credentials_path:
            raise ValueError("Google Vision credentials path must be specified when project ID is provided")
        
        return self

    class Config:
        env_file = ".env.online"
        case_sensitive = False
        use_enum_values = True

    def get_llm_provider_config(self, provider: str) -> LLMProviderConfig:
        """Get LLM provider configuration."""
        if provider == ProviderType.OPENAI:
            return LLMProviderConfig(
                api_key=self.openai_api_key,
                organization=self.openai_organization,
                model=self.openai_model,
                max_tokens=self.openai_max_tokens,
                temperature=self.openai_temperature
            )
        elif provider == ProviderType.MISTRAL:
            return LLMProviderConfig(
                api_key=self.mistral_api_key,
                model=self.mistral_model,
                max_tokens=self.mistral_max_tokens,
                temperature=self.mistral_temperature
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def get_ocr_provider_config(self, provider: str) -> OCRProviderConfig:
        """Get OCR provider configuration."""
        if provider == ProviderType.AZURE_VISION:
            return OCRProviderConfig(
                key=self.azure_vision_key,
                endpoint=self.azure_vision_endpoint,
                region=self.azure_vision_region
            )
        elif provider == ProviderType.GOOGLE_VISION:
            return OCRProviderConfig(
                project_id=self.google_vision_project_id,
                credentials_path=self.google_vision_credentials_path
            )
        else:
            raise ValueError(f"Unsupported OCR provider: {provider}")

    def get_vector_store_config(self, provider: str) -> VectorStoreConfig:
        """Get vector store provider configuration."""
        if provider == ProviderType.PINECONE:
            return VectorStoreConfig(
                api_key=self.pinecone_api_key,
                environment=self.pinecone_environment
            )
        elif provider == ProviderType.WEAVIATE:
            return VectorStoreConfig(
                url=self.weaviate_url,
                api_key=self.weaviate_api_key,
                username=self.weaviate_username,
                password=self.weaviate_password
            )
        else:
            raise ValueError(f"Unsupported vector store provider: {provider}")

    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available."""
        try:
            if provider in [ProviderType.OPENAI, ProviderType.MISTRAL]:
                return self.get_llm_provider_config(provider).is_available()
            elif provider in [ProviderType.AZURE_VISION, ProviderType.GOOGLE_VISION]:
                return self.get_ocr_provider_config(provider).is_available()
            elif provider in [ProviderType.PINECONE, ProviderType.WEAVIATE]:
                return self.get_vector_store_config(provider).is_available()
            else:
                return False
        except ValueError:
            return False

    def get_available_providers(self) -> Dict[str, bool]:
        """Get all available providers and their status."""
        providers = list(ProviderType)
        return {provider: self.is_provider_available(provider) for provider in providers}

    def get_provider_priorities(self) -> Dict[str, List[str]]:
        """Get provider priorities for different services."""
        return {
            "llm": self.llm_provider_priority,
            "ocr": self.ocr_provider_priority,
            "vector_store": self.vector_store_priority
        }

    def get_first_available_provider(self, provider_type: str) -> Optional[str]:
        """Get the first available provider of the specified type."""
        if provider_type == "llm":
            providers = self.llm_provider_priority
        elif provider_type == "ocr":
            providers = self.ocr_provider_priority
        elif provider_type == "vector_store":
            providers = self.vector_store_priority
        else:
            return None
        
        for provider in providers:
            if self.is_provider_available(provider):
                return provider
        return None


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings singleton instance.
    
    Returns:
        Settings: The application settings instance.
    """
    return Settings()


# Backward compatibility functions
def get_provider_config(provider_name: str, settings: Optional[Settings] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific provider (legacy function).
    
    Args:
        provider_name: Name of the provider
        settings: Optional settings instance
        
    Returns:
        Dict containing provider configuration
    """
    settings = settings or get_settings()
    
    try:
        if provider_name in [ProviderType.OPENAI, ProviderType.MISTRAL]:
            config = settings.get_llm_provider_config(provider_name)
            return {
                "api_key": config.api_key,
                "organization": config.organization,
                "model": config.model,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }
        elif provider_name in [ProviderType.AZURE_VISION, ProviderType.GOOGLE_VISION]:
            config = settings.get_ocr_provider_config(provider_name)
            return {
                "key": config.key,
                "endpoint": config.endpoint,
                "region": config.region,
                "project_id": config.project_id,
                "credentials_path": config.credentials_path
            }
        elif provider_name in [ProviderType.PINECONE, ProviderType.WEAVIATE]:
            config = settings.get_vector_store_config(provider_name)
            return {
                "api_key": config.api_key,
                "url": config.url,
                "environment": config.environment,
                "username": config.username,
                "password": config.password
            }
        else:
            return {}
    except ValueError:
        return {}


def is_provider_available(provider_name: str, settings: Optional[Settings] = None) -> bool:
    """
    Check if a provider is available (legacy function).
    
    Args:
        provider_name: Name of the provider
        settings: Optional settings instance
        
    Returns:
        True if provider is available, False otherwise
    """
    settings = settings or get_settings()
    return settings.is_provider_available(provider_name)


def get_available_providers(settings: Optional[Settings] = None) -> Dict[str, bool]:
    """
    Get all available providers and their status (legacy function).
    
    Args:
        settings: Optional settings instance
        
    Returns:
        Dict mapping provider names to availability status
    """
    settings = settings or get_settings()
    return settings.get_available_providers()


def get_provider_priorities(settings: Optional[Settings] = None) -> Dict[str, List[str]]:
    """
    Get provider priorities for different services (legacy function).
    
    Args:
        settings: Optional settings instance
        
    Returns:
        Dict mapping service types to provider priority lists
    """
    settings = settings or get_settings()
    return settings.get_provider_priorities() 