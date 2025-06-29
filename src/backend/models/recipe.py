"""
Recipe model for cooking features.
Zapewnia model przepisów kulinarnych z pełną separacją.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base


class Recipe(Base):
    """Recipe model for cooking recipes."""
    
    __tablename__ = "recipes"
    
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    ingredients = Column(JSON, nullable=False)  # lista składników z ilościami
    instructions = Column(Text, nullable=False)
    cooking_time = Column(Integer, nullable=True)  # w minutach
    difficulty = Column(String(20), nullable=True)  # łatwy, średni, trudny
    servings = Column(Integer, nullable=True)
    calories_per_serving = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)  # kuchnia włoska, wegetariańska, etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_ai_generated = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="recipes")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Recipe(id={self.id}, name='{self.name}', difficulty='{self.difficulty}')>" 