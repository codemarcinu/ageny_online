"""
Main FastAPI application for Ageny Online.
Główna aplikacja FastAPI z konfiguracją i routingiem z pełną separacją.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

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
