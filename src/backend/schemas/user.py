"""
User schemas for Ageny Online.
Zapewnia walidację danych użytkownika z pełną separacją.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator, constr


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    
    @validator('username')
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.strip():
            raise ValueError('Username cannot be empty')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.strip()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: constr(min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not v.strip():
            raise ValueError('Password cannot be empty')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user data."""
    
    username: Optional[constr(min_length=3, max_length=50)] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError('Username cannot be empty')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
            return v.strip()
        return v


class UserResponse(UserBase):
    """Schema for user response data."""
    
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    preferences: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 