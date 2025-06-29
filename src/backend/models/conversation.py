"""
Conversation and Message models for Ageny Online.
Zapewnia modele konwersacji z pełną separacją.
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from .base import Base


class Conversation(Base):
    """Conversation model for chat sessions."""
    
    __tablename__ = "conversations"
    
    title = Column(String(200), nullable=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_type = Column(String(50), nullable=False)
    provider_used = Column(String(50), nullable=True)
    meta_data = Column(JSON, nullable=True)
    
    # Relationships - using class names only
    user = relationship(
        "User",
        back_populates="conversations"
    )
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Conversation(id={self.id}, session_id='{self.session_id}', agent_type='{self.agent_type}')>"


class Message(Base):
    """Message model for individual chat messages."""
    
    __tablename__ = "messages"
    
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    provider_used = Column(String(50), nullable=True)
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(String(20), nullable=True)  # Store as string to avoid precision issues
    processing_time = Column(String(20), nullable=True)  # Store as string
    meta_data = Column(JSON, nullable=True)
    
    # Relationships - using class names only
    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>" 