"""
Custom exceptions for Ageny Online.
Zapewnia hierarchię wyjątków z pełną separacją od my_assistant.
"""

from .base import AgenyOnlineError
from .agent import AgentError, UnsupportedAgentTypeError
from .ocr import OCRError, OCRProviderError
from .database import DatabaseError, ValidationError
from .auth import AuthenticationError, AuthorizationError

__all__ = [
    "AgenyOnlineError",
    "AgentError",
    "UnsupportedAgentTypeError", 
    "OCRError",
    "OCRProviderError",
    "DatabaseError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError"
] 