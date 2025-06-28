"""
OCR exceptions for Ageny Online.
Zapewnia wyjątki OCR z pełną separacją.
"""

from .base import AgenyOnlineError


class OCRError(AgenyOnlineError):
    """Base exception for OCR operations."""
    
    def __init__(self, message: str, provider: str = None, **kwargs):
        super().__init__(message, error_code="OCR_ERROR", **kwargs)
        self.provider = provider


class OCRProviderError(OCRError):
    """Raised when OCR provider fails."""
    
    def __init__(self, message: str, provider: str, status_code: int = None):
        super().__init__(
            message=message,
            provider=provider,
            error_code="OCR_PROVIDER_ERROR",
            details={"status_code": status_code}
        )
        self.status_code = status_code 