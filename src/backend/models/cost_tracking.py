"""
Cost tracking model for Ageny Online.
Zapewnia model śledzenia kosztów z pełną separacją.
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship

from .base import Base


class CostRecord(Base):
    """Cost tracking model for monitoring API usage costs."""
    
    __tablename__ = "cost_records"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    service_type = Column(String(50), nullable=False)  # chat, ocr, embedding, etc.
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(String(20), nullable=False)  # Store as string to avoid precision issues
    request_count = Column(Integer, default=1, nullable=False)
    meta_data = Column(JSON, nullable=True)
    
    # Relationships - using full module paths to prevent conflicts
    user = relationship("src.backend.models.user.User")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CostRecord(id={self.id}, provider='{self.provider}', cost='{self.cost}', date={self.date})>" 