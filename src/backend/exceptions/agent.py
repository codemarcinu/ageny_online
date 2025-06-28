"""
Agent exceptions for Ageny Online.
Zapewnia wyjątki agentów z pełną separacją.
"""

from .base import AgenyOnlineError


class AgentError(AgenyOnlineError):
    """Base exception for agent operations."""
    
    def __init__(self, message: str, agent_type: str = None, **kwargs):
        super().__init__(message, error_code="AGENT_ERROR", **kwargs)
        self.agent_type = agent_type


class UnsupportedAgentTypeError(AgentError):
    """Raised when an unsupported agent type is requested."""
    
    def __init__(self, agent_type: str, available_types: list = None):
        message = f"Unsupported agent type: {agent_type}"
        if available_types:
            message += f". Available types: {', '.join(available_types)}"
        
        super().__init__(
            message=message,
            agent_type=agent_type,
            error_code="UNSUPPORTED_AGENT_TYPE",
            details={"available_types": available_types or []}
        ) 