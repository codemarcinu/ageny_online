"""
ShoppingList model for cooking features.
Zapewnia model list zakupów z pełną separacją.
"""

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship

from .base import Base


class ShoppingList(Base):
    """ShoppingList model for shopping lists."""
    
    __tablename__ = "shopping_lists"
    
    name = Column(String(100), nullable=False, index=True)
    items = Column(JSON, nullable=False)  # lista produktów z ilościami
    total_estimated_cost = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="shopping_lists")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<ShoppingList(id={self.id}, name='{self.name}', completed={self.is_completed})>" 