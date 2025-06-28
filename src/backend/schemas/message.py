"""
Message schemas for Ageny Online.
Zapewnia walidację danych wiadomości z pełną separacją.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, constr


class MessageBase(BaseModel):
    """Base message schema with common fields."""
    
    conversation_id: int
    role: constr(min_length=1, max_length=20)  # user, assistant, system
    content: constr(min_length=1)
    provider_used: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[str] = None
    processing_time: Optional[str] = None
    metadata: Optional[dict] = None
    
    @validator('role')
    def validate_role(cls, v: str) -> str:
        """Validate message role."""
        valid_roles = ['user', 'assistant', 'system']
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {valid_roles}')
        return v
    
    @validator('content')
    def validate_content(cls, v: str) -> str:
        """Validate message content."""
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    pass


class MessageResponse(MessageBase):
    """Schema for message response data."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 