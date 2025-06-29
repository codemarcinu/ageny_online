"""
Product model for cooking features.
Zapewnia model produktów spożywczych z pełną separacją.
"""

from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Product(Base):
    """Product model for food items."""
    
    __tablename__ = "products"
    
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # warzywa, mięso, nabiał, etc.
    unit = Column(String(20), nullable=False)  # kg, szt, l, etc.
    price_per_unit = Column(Float, nullable=True)
    calories_per_100g = Column(Integer, nullable=True)
    proteins = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="products")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Product(id={self.id}, name='{self.name}', category='{self.category}')>" 