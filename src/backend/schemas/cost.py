"""
Cost tracking schemas for Ageny Online.
Zapewnia walidację danych kosztów z pełną separacją.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, validator, constr


class CostRecordBase(BaseModel):
    """Base cost record schema with common fields."""
    
    date: date
    provider: constr(min_length=1, max_length=50)
    service_type: constr(min_length=1, max_length=50)  # chat, ocr, embedding, etc.
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: constr(min_length=1, max_length=20)
    request_count: int = 1
    metadata: Optional[dict] = None
    
    @validator('service_type')
    def validate_service_type(cls, v: str) -> str:
        """Validate service type."""
        valid_types = ['chat', 'ocr', 'embedding', 'vision', 'other']
        if v not in valid_types:
            raise ValueError(f'Service type must be one of: {valid_types}')
        return v
    
    @validator('cost')
    def validate_cost(cls, v: str) -> str:
        """Validate cost format."""
        try:
            float(v)
        except ValueError:
            raise ValueError('Cost must be a valid number')
        return v


class CostRecordCreate(CostRecordBase):
    """Schema for creating a new cost record."""
    
    user_id: Optional[int] = None


class CostRecordResponse(CostRecordBase):
    """Schema for cost record response data."""
    
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        } 