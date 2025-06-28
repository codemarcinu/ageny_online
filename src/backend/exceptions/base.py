"""
Base exceptions for Ageny Online.
Zapewnia bazowe wyjątki z pełną separacją.
"""


class AgenyOnlineError(Exception):
    """Base exception for Ageny Online application."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(message='{self.message}', error_code='{self.error_code}')>" 