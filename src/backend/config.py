import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env.online file
load_dotenv(".env.online")

class Settings(BaseSettings):
    """Application settings for Ageny Online."""
    
    # API Configuration
    api_title: str = "Ageny Online API"
    api_version: str = "1.0.0"
    api_description: str = "Online AI Agents API with external LLM and OCR providers"
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS Configuration
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    
    # Rate Limiting
    rate_limit_default: str = Field(default="100/minute", env="RATE_LIMIT_DEFAULT")
    rate_limit_strict: str = Field(default="10/minute", env="RATE_LIMIT_STRICT")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Mistral Configuration
    mistral_api_key: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")
    mistral_model: str = Field(default="mistral-large-latest", env="MISTRAL_MODEL")
    mistral_max_tokens: int = Field(default=1000, env="MISTRAL_MAX_TOKENS")
    mistral_temperature: float = Field(default=0.7, env="MISTRAL_TEMPERATURE")
    
    # Azure Vision Configuration
    azure_vision_key: Optional[str] = Field(default=None, env="AZURE_VISION_KEY")
    azure_vision_endpoint: Optional[str] = Field(default=None, env="AZURE_VISION_ENDPOINT")
    azure_vision_region: Optional[str] = Field(default=None, env="AZURE_VISION_REGION")
    
    # Google Vision Configuration
    google_vision_key: Optional[str] = Field(default=None, env="GOOGLE_VISION_KEY")
    google_vision_project_id: Optional[str] = Field(default=None, env="GOOGLE_VISION_PROJECT_ID")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Cost Tracking
    enable_cost_tracking: bool = Field(default=True, env="ENABLE_COST_TRACKING")
    
    # File Upload Configuration
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_image_types: list = Field(default=["image/jpeg", "image/png", "image/gif", "image/webp"])
    
    # Batch Processing Configuration
    max_batch_size: int = Field(default=10, env="MAX_BATCH_SIZE")
    batch_timeout: int = Field(default=300, env="BATCH_TIMEOUT")  # 5 minutes
    
    class Config:
        env_file = ".env.online"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Helper functions
def get_provider_config(provider_name: str) -> Dict[str, Any]:
    """Get configuration for a specific provider."""
    configs = {
        "openai": {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "max_tokens": settings.openai_max_tokens,
            "temperature": settings.openai_temperature
        },
        "mistral": {
            "api_key": settings.mistral_api_key,
            "model": settings.mistral_model,
            "max_tokens": settings.mistral_max_tokens,
            "temperature": settings.mistral_temperature
        },
        "azure_vision": {
            "key": settings.azure_vision_key,
            "endpoint": settings.azure_vision_endpoint,
            "region": settings.azure_vision_region
        },
        "google_vision": {
            "key": settings.google_vision_key,
            "project_id": settings.google_vision_project_id
        }
    }
    return configs.get(provider_name, {})

def is_provider_available(provider_name: str) -> bool:
    """Check if a provider is available (has required configuration)."""
    config = get_provider_config(provider_name)
    
    if provider_name in ["openai", "mistral"]:
        return bool(config.get("api_key"))
    elif provider_name == "azure_vision":
        return bool(config.get("key") and config.get("endpoint"))
    elif provider_name == "google_vision":
        return bool(config.get("key") and config.get("project_id"))
    
    return False

def get_available_providers() -> Dict[str, bool]:
    """Get all available providers and their status."""
    providers = ["openai", "mistral", "azure_vision", "google_vision"]
    return {provider: is_provider_available(provider) for provider in providers}
