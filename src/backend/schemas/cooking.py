"""
Cooking schemas for Ageny Online.
Zapewnia walidację danych kulinarnych z pełną separacją.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# Product Schemas
class ProductBase(BaseModel):
    """Base product schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Nazwa produktu")
    category: str = Field(..., min_length=1, max_length=50, description="Kategoria produktu")
    unit: str = Field(..., min_length=1, max_length=20, description="Jednostka miary")
    price_per_unit: Optional[float] = Field(None, ge=0, description="Cena za jednostkę")
    calories_per_100g: Optional[int] = Field(None, ge=0, description="Kalorie na 100g")
    proteins: Optional[float] = Field(None, ge=0, description="Białka na 100g")
    carbs: Optional[float] = Field(None, ge=0, description="Węglowodany na 100g")
    fats: Optional[float] = Field(None, ge=0, description="Tłuszcze na 100g")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating product data."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    price_per_unit: Optional[float] = Field(None, ge=0)
    calories_per_100g: Optional[int] = Field(None, ge=0)
    proteins: Optional[float] = Field(None, ge=0)
    carbs: Optional[float] = Field(None, ge=0)
    fats: Optional[float] = Field(None, ge=0)


class ProductResponse(ProductBase):
    """Schema for product response data."""
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


# Recipe Schemas
class IngredientSchema(BaseModel):
    """Schema for recipe ingredient."""
    
    name: str = Field(..., description="Nazwa składnika")
    amount: str = Field(..., description="Ilość")
    unit: str = Field(..., description="Jednostka")


class RecipeBase(BaseModel):
    """Base recipe schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Nazwa przepisu")
    description: Optional[str] = Field(None, description="Opis przepisu")
    ingredients: List[Dict[str, Any]] = Field(..., description="Lista składników")
    instructions: str = Field(..., min_length=1, description="Instrukcje przygotowania")
    cooking_time: Optional[int] = Field(None, ge=0, description="Czas gotowania w minutach")
    difficulty: Optional[str] = Field(None, description="Poziom trudności")
    servings: Optional[int] = Field(None, ge=1, description="Liczba porcji")
    calories_per_serving: Optional[int] = Field(None, ge=0, description="Kalorie na porcję")
    tags: Optional[List[str]] = Field(None, description="Tagi przepisu")


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe."""
    pass


class RecipeUpdate(BaseModel):
    """Schema for updating recipe data."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    ingredients: Optional[List[Dict[str, Any]]] = None
    instructions: Optional[str] = Field(None, min_length=1)
    cooking_time: Optional[int] = Field(None, ge=0)
    difficulty: Optional[str] = None
    servings: Optional[int] = Field(None, ge=1)
    calories_per_serving: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None


class RecipeResponse(RecipeBase):
    """Schema for recipe response data."""
    
    id: int
    user_id: int
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


# Shopping List Schemas
class ShoppingItemSchema(BaseModel):
    """Schema for shopping list item."""
    
    product_name: str = Field(..., description="Nazwa produktu")
    quantity: float = Field(..., ge=0, description="Ilość")
    unit: str = Field(..., description="Jednostka")
    estimated_price: Optional[float] = Field(None, ge=0, description="Szacowana cena")
    is_purchased: bool = Field(False, description="Czy kupione")


class ShoppingListBase(BaseModel):
    """Base shopping list schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Nazwa listy zakupów")
    items: List[Dict[str, Any]] = Field(..., description="Lista produktów")


class ShoppingListCreate(ShoppingListBase):
    """Schema for creating a new shopping list."""
    budget: Optional[float] = Field(None, ge=0, description="Budżet na zakupy")


class ShoppingListUpdate(BaseModel):
    """Schema for updating shopping list data."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    items: Optional[List[Dict[str, Any]]] = None
    is_completed: Optional[bool] = None


class ShoppingListResponse(ShoppingListBase):
    """Schema for shopping list response data."""
    
    id: int
    user_id: int
    total_estimated_cost: Optional[float]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


# AI Request Schemas
class RecipeGenerationRequest(BaseModel):
    """Schema for AI recipe generation request."""
    
    ingredients: List[str] = Field(..., description="Lista dostępnych składników")
    preferences: Optional[str] = Field(None, description="Preferencje kulinarne")
    cuisine_type: Optional[str] = Field(None, description="Typ kuchni")
    difficulty: Optional[str] = Field(None, description="Poziom trudności")
    cooking_time: Optional[int] = Field(None, ge=0, description="Maksymalny czas gotowania")


class ShoppingListOptimizationRequest(BaseModel):
    """Schema for AI shopping list optimization request."""
    
    items: List[Dict[str, Any]] = Field(..., description="Lista produktów do optymalizacji")
    budget: Optional[float] = Field(None, ge=0, description="Budżet na zakupy")
    preferences: Optional[str] = Field(None, description="Preferencje zakupowe")


# Search and Filter Schemas
class ProductSearchRequest(BaseModel):
    """Schema for product search request."""
    
    query: Optional[str] = Field(None, description="Wyszukiwana fraza")
    category: Optional[str] = Field(None, description="Filtrowanie po kategorii")
    min_price: Optional[float] = Field(None, ge=0, description="Minimalna cena")
    max_price: Optional[float] = Field(None, ge=0, description="Maksymalna cena")


class RecipeSearchRequest(BaseModel):
    """Schema for recipe search request."""
    
    query: Optional[str] = Field(None, description="Wyszukiwana fraza")
    tags: Optional[List[str]] = Field(None, description="Filtrowanie po tagach")
    difficulty: Optional[str] = Field(None, description="Poziom trudności")
    max_cooking_time: Optional[int] = Field(None, ge=0, description="Maksymalny czas gotowania")
    max_calories: Optional[int] = Field(None, ge=0, description="Maksymalne kalorie na porcję")


# Response Schemas
class CookingStatsResponse(BaseModel):
    """Schema for cooking statistics response."""
    
    total_products: int
    total_recipes: int
    total_shopping_lists: int
    completed_shopping_lists: int
    total_spent: float
    favorite_categories: List[str]
    recent_recipes: List[Dict[str, Any]]
    recent_shopping_lists: List[Dict[str, Any]] 