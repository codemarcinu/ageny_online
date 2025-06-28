"""
OCR schemas for Ageny Online.
Zapewnia walidację danych OCR z pełną separacją.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, constr


class OCRRequest(BaseModel):
    """Schema for OCR request data."""
    
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt: Optional[str] = None
    
    @validator('provider')
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        """Validate OCR provider."""
        if v is not None:
            valid_providers = ['mistral_vision', 'azure_vision', 'google_vision']
            if v not in valid_providers:
                raise ValueError(f'Provider must be one of: {valid_providers}')
        return v


class OCRResponse(BaseModel):
    """Schema for OCR response data."""
    
    text: str
    confidence: float
    provider: str
    model_used: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: dict
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class OCRBatchResponse(BaseModel):
    """Schema for OCR batch response data."""
    
    results: List[OCRResponse]
    total_cost: float
    total_tokens: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True 