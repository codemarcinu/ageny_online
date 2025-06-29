<<<<<<< HEAD
"""
Main FastAPI application for Ageny Online.
Główna aplikacja FastAPI z konfiguracją i routingiem z pełną separacją.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

=======
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.agents.base_agent import GeneralConversationAgent, AgentContext
from backend.core.llm_providers.provider_factory import provider_factory
from backend.database import get_async_session, create_tables
from backend.exceptions import AgenyOnlineError

# Import OCR endpoints
from backend.api.v2.endpoints.ocr import router as ocr_router
# Import Chat endpoints
from backend.api.v2.endpoints.chat import router as chat_router
# Import Web Search endpoints
from backend.api.v2.endpoints.web_search import router as web_search_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global agent instances
general_agent: GeneralConversationAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Ageny Online application...")
    
    # Initialize database tables
    try:
        await create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise
    
    # Initialize agents
    global general_agent
    general_agent = GeneralConversationAgent()
    
    # Check provider health
    health_status = await provider_factory.health_check_all()
    logger.info(f"Provider health status: {health_status}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ageny Online application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Assistant with external API providers",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
=======
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
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Add Prometheus metrics
if settings.ENABLE_METRICS:
    Instrumentator().instrument(app).expose(app)


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        # Check agent health
        agent_health = await general_agent.health_check()
        
        # Check provider health
        provider_health = await provider_factory.health_check_all()
        
        return {
            "status": "healthy" if agent_health["status"] == "healthy" else "unhealthy",
            "app": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
            },
            "agent": agent_health,
            "providers": provider_health,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@app.get("/api/v1/chat")
@limiter.limit(f"{settings.RATE_LIMIT_CHAT}/minute")
async def chat_endpoint(
    request: Request,
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Chat endpoint for general conversation.
    
    Args:
        message: User message
        session_id: Session identifier
        user_id: User identifier
        
    Returns:
        AI response
    """
    try:
        # Create context
        context = AgentContext(
            user_id=user_id,
            session_id=session_id,
            request_id=str(request.state.request_id) if hasattr(request.state, 'request_id') else None,
        )
        
        # Process query
        response = await general_agent.process_query(message, context=context)
        
        return {
            "success": response.success,
            "response": response.content,
            "agent_type": response.agent_type,
            "provider_used": response.provider_used,
            "processing_time": response.processing_time,
            "metadata": response.metadata,
        }
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat")
@limiter.limit(f"{settings.RATE_LIMIT_CHAT}/minute")
async def chat_post_endpoint(
    request: Request,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Chat endpoint (POST) for general conversation.
    
    Args:
        data: Request data with message and optional context
        
    Returns:
        AI response
    """
    try:
        message = data.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Create context
        context = AgentContext(
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            request_id=str(request.state.request_id) if hasattr(request.state, 'request_id') else None,
            metadata=data.get("metadata", {}),
        )
        
        # Process query
        response = await general_agent.process_query(message, context=context)
        
        return {
            "success": response.success,
            "response": response.content,
            "agent_type": response.agent_type,
            "provider_used": response.provider_used,
            "processing_time": response.processing_time,
            "metadata": response.metadata,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat POST endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/providers")
async def get_providers() -> Dict[str, Any]:
    """Get available providers information"""
    try:
        available_providers = provider_factory.get_available_providers()
        configured_providers = provider_factory.get_configured_providers()
        
        provider_info = {}
        for provider_type in available_providers:
            provider_info[provider_type.value] = {
                "available": True,
                "configured": provider_type in configured_providers,
                "priority": provider_factory.get_provider_priority(provider_type),
            }
        
        return {
            "available_providers": [p.value for p in available_providers],
            "configured_providers": [p.value for p in configured_providers],
            "provider_details": provider_info,
        }
        
    except Exception as e:
        logger.error(f"Get providers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agents")
async def get_agents() -> Dict[str, Any]:
    """Get available agents information"""
    try:
        return {
            "agents": [
                {
                    "type": general_agent.config.agent_type,
                    "name": general_agent.config.name,
                    "description": general_agent.config.description,
                    "enabled": general_agent.config.enabled,
                    "stats": general_agent.get_stats(),
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Get agents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include OCR endpoints
app.include_router(ocr_router, prefix="/api/v2")
# Include Chat endpoints
app.include_router(chat_router, prefix="/api/v2")
# Include Web Search endpoints
app.include_router(web_search_router, prefix="/api/v2")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    
    # Handle custom exceptions
    if isinstance(exc, AgenyOnlineError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": exc.message,
                "error_code": exc.error_code,
                "details": exc.details
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.UVICORN_RELOAD,
        reload_dirs=settings.UVICORN_RELOAD_DIRS.split(",") if settings.UVICORN_RELOAD_DIRS else None,
    ) 
=======
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
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
