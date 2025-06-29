"""
Main FastAPI application for Ageny Online.
Główna aplikacja FastAPI z konfiguracją i routingiem z pełną separacją.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path
import time

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
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
# Import Gamification endpoints
from backend.api.v2.endpoints.gamification import router as gamification_router
# Import Profile endpoints
from backend.api.v2.endpoints.profile import router as profile_router
# Import Vector Store endpoints
from backend.api.v2.endpoints.vector_store import router as vector_store_router

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging to both file and console
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "backend.log"),
        logging.StreamHandler()
    ]
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "message": "Ageny Online API",
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "endpoints": [
            "/health",
            "/api/v1/chat",
            "/api/v1/providers",
            "/api/v1/agents",
            "/api/v2/chat/chat",
            "/api/v2/ocr/extract-text",
            "/api/v2/web-search/search"
        ]
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        # Initialize agent if not already done
        global general_agent
        if 'general_agent' not in globals() or general_agent is None:
            general_agent = GeneralConversationAgent()
        
        # Check agent health
        agent_health = await general_agent.health_check()
        
        # Check provider health
        provider_health = await provider_factory.health_check_all()
        
        # Get available providers
        available_providers = provider_factory.get_available_providers()
        configured_providers = provider_factory.get_configured_providers()
        
        # Format provider info
        llm_providers = {}
        for provider_type in available_providers:
            llm_providers[provider_type.value] = {
                "available": True,
                "configured": provider_type in configured_providers,
                "priority": provider_factory.get_provider_priority(provider_type),
            }
        
        return {
            "status": "healthy" if agent_health["status"] == "healthy" else "unhealthy",
            "app": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
            },
            "agent": agent_health,
            "llm_providers": llm_providers,
            "ocr_providers": {},  # TODO: Add OCR provider health check
            "vector_stores": {},  # TODO: Add vector store health check
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "llm_providers": {},
            "ocr_providers": {},
            "vector_stores": {},
            "timestamp": time.time(),
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
            "llm_providers": provider_info,
            "ocr_providers": {},  # TODO: Add OCR providers
            "vector_stores": {},  # TODO: Add vector stores
            "priorities": {
                "llm": provider_factory.get_provider_priorities(),
                "ocr": {},
                "vector": {}
            },
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


@app.post("/api/v1/setup")
async def setup_providers() -> Dict[str, Any]:
    """Setup providers endpoint"""
    try:
        # Mock setup process
        return {
            "status": "success",
            "success": True,
            "message": "Providers setup completed",
            "providers_configured": len(provider_factory.get_configured_providers()),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/costs")
async def get_cost_info() -> Dict[str, Any]:
    """Get cost information endpoint"""
    try:
        return {
            "total_cost": 0.0,
            "cost_breakdown": {
                "llm": 0.0,
                "ocr": 0.0,
                "vector_store": 0.0
            },
            "llm_providers": {
                "openai": {"cost": 0.0, "requests": 0},
                "mistral": {"cost": 0.0, "requests": 0},
                "anthropic": {"cost": 0.0, "requests": 0}
            },
            "currency": "USD",
            "period": "all_time",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Cost info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def make_teen_friendly(text: str) -> str:
    """Placeholder for teen-friendly formatting (add emoji, simplify, etc.)."""
    if not text:
        return text
    # Example: add a smiley and make it more casual
    return text + " 😊"

@app.middleware("http")
async def teen_friendly_middleware(request: Request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        try:
            data = json.loads(body)
            if isinstance(data, dict) and "response" in data:
                data["response"] = make_teen_friendly(data["response"])
                return JSONResponse(content=data, status_code=response.status_code)
        except Exception:
            pass  # fallback to original response
        return JSONResponse(content=json.loads(body), status_code=response.status_code)
    return response


# Include OCR endpoints
app.include_router(ocr_router, prefix="/api/v2")
# Include Chat endpoints
app.include_router(chat_router, prefix="/api/v2")
# Include Web Search endpoints
app.include_router(web_search_router, prefix="/api/v2")
# Include Gamification endpoints
app.include_router(gamification_router, prefix="/api/v2")
# Include Profile endpoints
app.include_router(profile_router, prefix="/api/v2")
# Include Vector Store endpoints
app.include_router(vector_store_router, prefix="/api/v2")


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
