from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import os
from typing import Dict, Any

# Import our modules
from ..config import get_settings, get_available_providers, get_provider_priorities
from ..core.llm_providers.provider_factory import llm_factory, ProviderType, ProviderConfig
from ..core.ocr_providers.ocr_factory import ocr_factory, OCRProviderType, OCRProviderConfig
from .v2.endpoints import ocr, chat, vector_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings instance
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Ageny Online API",
    description="Online AI Agents API with external LLM and OCR providers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(ocr.router, prefix="/api/v2/ocr", tags=["OCR"])
app.include_router(chat.router, prefix="/api/v2/chat", tags=["Chat"])
app.include_router(vector_store.router, prefix="/api/v2/vector-store", tags=["Vector Store"])

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint with basic API information."""
    return {
        "message": "Ageny Online API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/v2/chat",
            "ocr": "/api/v2/ocr", 
            "vector_store": "/api/v2/vector-store"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if providers are available
        available_llms = llm_factory.get_available_providers()
        available_ocrs = ocr_factory.get_available_providers()
        
        # Check vector stores
        vector_store_status = {
            "pinecone": bool(settings.pinecone_api_key),
            "weaviate": bool(settings.weaviate_url)
        }
        
        return {
            "status": "healthy",
            "llm_providers": available_llms,
            "ocr_providers": available_ocrs,
            "vector_stores": vector_store_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/api/v1/providers")
@limiter.limit("30/minute")
async def get_providers(request: Request):
    """Get available LLM and OCR providers."""
    try:
        return {
            "llm_providers": llm_factory.get_available_providers(),
            "ocr_providers": ocr_factory.get_available_providers(),
            "vector_stores": {
                "pinecone": bool(settings.pinecone_api_key),
                "weaviate": bool(settings.weaviate_url)
            },
            "priorities": get_provider_priorities()
        }
    except Exception as e:
        logger.error(f"Failed to get providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get providers")

@app.post("/api/v1/setup")
async def setup_providers():
    """Setup and configure all available providers."""
    try:
        # Setup LLM providers
        if settings.openai_api_key:
            llm_factory.register_provider(
                ProviderType.OPENAI,
                ProviderConfig(
                    api_key=settings.openai_api_key,
                    organization=settings.openai_organization,
                    priority=1
                )
            )
        
        if settings.mistral_api_key:
            llm_factory.register_provider(
                ProviderType.MISTRAL,
                ProviderConfig(
                    api_key=settings.mistral_api_key,
                    priority=2
                )
            )
        
        # Setup OCR providers
        if settings.azure_vision_key and settings.azure_vision_endpoint:
            ocr_factory.register_provider(
                OCRProviderType.AZURE_VISION,
                OCRProviderConfig(
                    azure_key=settings.azure_vision_key,
                    azure_endpoint=settings.azure_vision_endpoint,
                    azure_region=settings.azure_vision_region,
                    priority=1
                )
            )
        
        if settings.google_vision_project_id:
            ocr_factory.register_provider(
                OCRProviderType.GOOGLE_VISION,
                OCRProviderConfig(
                    google_project_id=settings.google_vision_project_id,
                    google_credentials_path=settings.google_vision_credentials_path,
                    priority=2
                )
            )
        
        return {
            "status": "success",
            "message": "Providers configured successfully",
            "llm_providers": llm_factory.get_available_providers(),
            "ocr_providers": ocr_factory.get_available_providers()
        }
        
    except Exception as e:
        logger.error(f"Failed to setup providers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup providers: {str(e)}")

@app.get("/api/v1/costs")
async def get_cost_info():
    """Get cost information for all providers."""
    try:
        costs = {
            "llm_providers": {},
            "ocr_providers": {},
            "vector_stores": {}
        }
        
        # Get LLM provider costs
        for provider_type in ProviderType:
            try:
                provider = llm_factory.get_provider(provider_type)
                if hasattr(provider, 'get_cost_info'):
                    costs["llm_providers"][provider_type.value] = provider.get_cost_info()
            except Exception:
                pass
        
        # Get OCR provider costs
        for provider_type in OCRProviderType:
            try:
                provider = ocr_factory.get_provider(provider_type)
                if hasattr(provider, 'get_cost_info'):
                    costs["ocr_providers"][provider_type.value] = provider.get_cost_info()
            except Exception:
                pass
        
        # Get vector store costs
        if settings.pinecone_api_key:
            try:
                from src.backend.core.vector_stores.pinecone_client import PineconeClient
                client = PineconeClient(settings.pinecone_api_key, settings.pinecone_environment)
                costs["vector_stores"]["pinecone"] = client.get_cost_info()
            except Exception:
                pass
        
        if settings.weaviate_url:
            try:
                from src.backend.core.vector_stores.weaviate_client import WeaviateClient
                client = WeaviateClient(settings.weaviate_url)
                costs["vector_stores"]["weaviate"] = client.get_cost_info()
            except Exception:
                pass
        
        return costs
        
    except Exception as e:
        logger.error(f"Failed to get cost info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cost info")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
