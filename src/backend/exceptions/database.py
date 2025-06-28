"""
Database exceptions for Ageny Online.
Zapewnia wyjątki bazy danych z pełną separacją.
"""

from .base import AgenyOnlineError


class DatabaseError(AgenyOnlineError):
    """Base exception for database operations."""
    
    def __init__(self, message: str, table: str = None, **kwargs):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)
        self.table = table


class ValidationError(DatabaseError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": value}
        )
        self.field = field
        self.value = value 