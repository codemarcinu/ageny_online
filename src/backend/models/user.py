"""
User model for Ageny Online.
Zapewnia model użytkownika z pełną separacją.
"""

from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    full_name = Column(String(100), nullable=True)
    preferences = Column(Text, nullable=True)  # JSON string
    
    # Relationships - using full module paths to prevent conflicts
    conversations = relationship(
        "src.backend.models.conversation.Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>" 