"""
Cost Tracking model for Ageny Online.
Zapewnia model śledzenia kosztów z pełną separacją.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class CostRecord(Base):
    """Cost Record model for tracking API usage costs."""
    
    __tablename__ = "cost_records"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=False)
    provider_type = Column(String(50), nullable=False)  # llm, ocr, vector_store
    provider_name = Column(String(50), nullable=False)  # openai, mistral, etc.
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=False, default=0.0)
    request_type = Column(String(50), nullable=False)  # chat, completion, embedding, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    meta_data = Column(String(500), nullable=True)  # Additional info as JSON string
    
    # Relationships - using class names only
    user = relationship("User", back_populates="cost_records")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CostRecord(id={self.id}, provider='{self.provider_name}', cost=${self.cost_usd})>" 