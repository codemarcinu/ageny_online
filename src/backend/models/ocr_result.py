"""
OCR Result model for Ageny Online.
Zapewnia model wyników OCR z pełną separacją.
"""

from sqlalchemy import Column, String, Text, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class OCRResult(Base):
    """OCR Result model for storing text extraction results."""
    
    __tablename__ = "ocr_results"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=False)
    provider_used = Column(String(50), nullable=False)
    model_used = Column(String(100), nullable=True)
    extracted_text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(String(20), nullable=True)  # Store as string to avoid precision issues
    image_size_bytes = Column(Integer, nullable=True)
    processing_time = Column(String(20), nullable=True)  # Store as string
    prompt_used = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)
    
    # Relationships - using full module paths to prevent conflicts
    user = relationship("src.backend.models.user.User")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<OCRResult(id={self.id}, provider='{self.provider_used}', confidence={self.confidence})>" 