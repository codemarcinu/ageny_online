"""
Authentication exceptions for Ageny Online.
Zapewnia wyjątki autoryzacji z pełną separacją.
"""

from .base import AgenyOnlineError


class AuthenticationError(AgenyOnlineError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", user_id: str = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details={"user_id": user_id}
        )
        self.user_id = user_id


class AuthorizationError(AgenyOnlineError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Authorization failed", user_id: str = None, required_permission: str = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details={"user_id": user_id, "required_permission": required_permission}
        )
        self.user_id = user_id
        self.required_permission = required_permission 