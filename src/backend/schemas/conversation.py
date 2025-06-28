"""
Conversation schemas for Ageny Online.
Zapewnia walidację danych konwersacji z pełną separacją.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, constr


class ConversationBase(BaseModel):
    """Base conversation schema with common fields."""
    
    title: Optional[str] = None
    session_id: constr(min_length=1, max_length=100)
    agent_type: constr(min_length=1, max_length=50)
    provider_used: Optional[str] = None
    metadata: Optional[dict] = None
    
    @validator('session_id')
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID format."""
        if not v.strip():
            raise ValueError('Session ID cannot be empty')
        return v.strip()
    
    @validator('agent_type')
    def validate_agent_type(cls, v: str) -> str:
        """Validate agent type."""
        if not v.strip():
            raise ValueError('Agent type cannot be empty')
        return v.strip()


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    
    user_id: Optional[int] = None


class ConversationUpdate(BaseModel):
    """Schema for updating conversation data."""
    
    title: Optional[str] = None
    agent_type: Optional[constr(min_length=1, max_length=50)] = None
    provider_used: Optional[str] = None
    metadata: Optional[dict] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response data."""
    
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 