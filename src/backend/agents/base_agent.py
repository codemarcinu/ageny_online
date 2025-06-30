"""
Base Agent for AI operations.
Zapewnia podstawowy interfejs dla wszystkich agentów AI.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from backend.config import settings
from backend.core.llm_providers.provider_factory import provider_factory, ProviderType

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    
    agent_type: str
    name: str
    description: str
    enabled: bool = True
    priority: int = 1
    max_concurrent_requests: int = 10
    timeout_seconds: int = 30


class AgentContext(BaseModel):
    """Context for agent operations"""
    
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Response from an agent"""
    
    success: bool
    content: str
    agent_type: str
    provider_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """
    Base class for all AI agents.
    Zapewnia podstawowy interfejs dla wszystkich agentów AI.
    """
    
    def __init__(self, config: AgentConfig) -> None:
        """Initialize base agent"""
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self.request_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
        
        logger.info(f"Initialized agent: {config.name} ({config.agent_type})")
    
    @abstractmethod
    async def process_query(
        self, 
        query: str, 
        context: Optional[AgentContext] = None,
        **kwargs: Any
    ) -> AgentResponse:
        """
        Process a query using the agent.
        
        Args:
            query: User query to process
            context: Additional context for the query
            **kwargs: Additional parameters
            
        Returns:
            Agent response
        """
        pass
    
    async def _get_llm_provider(self, provider_type: Optional[ProviderType] = None) -> Any:
        """
        Get LLM provider for the agent.
        
        Args:
            provider_type: Specific provider type to use
            
        Returns:
            LLM provider instance
        """
        if provider_type:
            return provider_factory.create_provider(provider_type)
        
        # Get best available provider
        best_provider_type = provider_factory.get_best_provider()
        if not best_provider_type:
            raise Exception("No LLM provider available")
        
        return provider_factory.create_provider(best_provider_type)
    
    async def _execute_with_semaphore(self, coro) -> Any:
        """Execute coroutine with semaphore for concurrency control"""
        async with self.semaphore:
            return await coro
    
    async def _execute_with_timeout(self, coro, timeout: Optional[int] = None) -> Any:
        """Execute coroutine with timeout"""
        timeout = timeout or self.config.timeout_seconds
        return await asyncio.wait_for(coro, timeout=timeout)
    
    def _needs_rag(self, query: str) -> bool:
        """Check if query needs RAG processing"""
        # Simple heuristic - can be improved
        rag_keywords = ["search", "find", "document", "file", "knowledge", "information"]
        return any(keyword in query.lower() for keyword in rag_keywords)
    
    def _needs_ocr(self, query: str) -> bool:
        """Check if query needs OCR processing"""
        # Simple heuristic - can be improved
        ocr_keywords = ["image", "photo", "picture", "scan", "receipt", "document"]
        return any(keyword in query.lower() for keyword in ocr_keywords)
    
    def _select_provider(self, query: str) -> Optional[ProviderType]:
        """Select appropriate provider based on query"""
        # Simple selection logic - can be improved with ML
        if "code" in query.lower() or "programming" in query.lower():
            return ProviderType.OPENAI  # Better for code
        elif "analysis" in query.lower() or "reasoning" in query.lower():
            return ProviderType.ANTHROPIC  # Better for reasoning
        else:
            return None  # Use default selection
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        try:
            # Check if LLM provider is available
            provider = await self._get_llm_provider()
            provider_health = await provider.health_check()
            
            return {
                "status": "healthy" if provider_health.get("status") == "healthy" else "unhealthy",
                "agent_type": self.config.agent_type,
                "name": self.config.name,
                "enabled": self.config.enabled,
                "request_count": self.request_count,
                "error_count": self.error_count,
                "last_error": self.last_error,
                "provider_health": provider_health,
            }
        except Exception as e:
            logger.error(f"Health check failed for agent {self.config.name}: {e}")
            return {
                "status": "unhealthy",
                "agent_type": self.config.agent_type,
                "name": self.config.name,
                "error": str(e),
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "agent_type": self.config.agent_type,
            "name": self.config.name,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1),
            "last_error": self.last_error,
        }
    
    def reset_stats(self) -> None:
        """Reset agent statistics"""
        self.request_count = 0
        self.error_count = 0
        self.last_error = None
        logger.info(f"Reset stats for agent: {self.config.name}")


class GeneralConversationAgent(BaseAgent):
    """General conversation agent for basic chat interactions"""
    
    def __init__(self) -> None:
        config = AgentConfig(
            agent_type="general_conversation",
            name="General Conversation Agent",
            description="Handles general conversation and basic queries",
            priority=1,
        )
        super().__init__(config)
    
    async def process_query(
        self, 
        query: str, 
        context: Optional[AgentContext] = None,
        **kwargs: Any
    ) -> AgentResponse:
        """Process general conversation query"""
        start_time = time.time()
        
        try:
            self.request_count += 1
            
            # Get LLM provider
            provider = await self._get_llm_provider()
            
            # Prepare messages
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Provide clear, concise, and accurate responses."},
                {"role": "user", "content": query}
            ]
            
            # Generate response
            response_text = await self._execute_with_timeout(
                provider.chat(messages=messages, **kwargs)
            )
            
            processing_time = time.time() - start_time
            
            return AgentResponse(
                success=True,
                content=response_text,
                agent_type=self.config.agent_type,
                provider_used=getattr(provider, 'provider_type', provider.__class__.__name__),
                tokens_used=kwargs.get('tokens_used', 0),
                cost=kwargs.get('cost', 0.0),
                processing_time=processing_time,
                metadata={
                    "query_length": len(query),
                    "response_length": len(response_text),
                    "context": context.dict() if context else {}
                }
            )
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Error in general conversation agent: {e}")
            
            return AgentResponse(
                success=False,
                content=f"Sorry, I encountered an error: {str(e)}",
                agent_type=self.config.agent_type,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            ) 