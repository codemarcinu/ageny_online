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
from src.backend.config import settings
from src.backend.core.llm_providers.provider_factory import LLMProviderFactory
from src.backend.core.ocr_providers.ocr_factory import OCRProviderFactory
from src.backend.api.v2.endpoints import ocr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint with basic API information."""
    return {
        "message": "Ageny Online API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if providers are available
        llm_factory = LLMProviderFactory()
        ocr_factory = OCRProviderFactory()
        
        available_llms = llm_factory.get_available_providers()
        available_ocrs = ocr_factory.get_available_providers()
        
        return {
            "status": "healthy",
            "llm_providers": available_llms,
            "ocr_providers": available_ocrs,
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
        llm_factory = LLMProviderFactory()
        ocr_factory = OCRProviderFactory()
        
        return {
            "llm_providers": llm_factory.get_available_providers(),
            "ocr_providers": ocr_factory.get_available_providers()
        }
    except Exception as e:
        logger.error(f"Failed to get providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get providers")

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
