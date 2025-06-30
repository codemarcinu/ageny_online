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


# NEW: Extended schemas for Antonina's cooking features

class MealPlanRequest(BaseModel):
    """Schema for meal plan generation request."""
    
    age: int = Field(..., ge=10, le=18, description="Wiek")
    weight: float = Field(..., ge=30, le=100, description="Waga (kg)")
    height: float = Field(..., ge=120, le=200, description="Wzrost (cm)")
    activity_level: str = Field(..., description="Poziom aktywności")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Ograniczenia dietetyczne")
    preferences: Optional[str] = Field(None, description="Preferencje smakowe")
    budget_per_day: Optional[float] = Field(None, ge=0, description="Budżet dzienny")


class MealPlanResponse(BaseModel):
    """Schema for meal plan response."""
    
    daily_calories: int
    daily_proteins: float
    daily_carbs: float
    daily_fats: float
    meals: List[Dict[str, Any]]
    shopping_list: List[Dict[str, Any]]
    estimated_cost: float
    nutrition_tips: List[str]


class NutritionInfo(BaseModel):
    """Schema for nutrition information."""
    
    calories: float = Field(..., ge=0, description="Kalorie")
    proteins: float = Field(..., ge=0, description="Białka (g)")
    carbs: float = Field(..., ge=0, description="Węglowodany (g)")
    fats: float = Field(..., ge=0, description="Tłuszcze (g)")
    fiber: Optional[float] = Field(None, ge=0, description="Błonnik (g)")
    sugar: Optional[float] = Field(None, ge=0, description="Cukier (g)")


class RecipeNutritionRequest(BaseModel):
    """Schema for recipe nutrition analysis request."""
    
    recipe_id: int = Field(..., description="ID przepisu")


class RecipeNutritionResponse(BaseModel):
    """Schema for recipe nutrition analysis response."""
    
    recipe_name: str
    total_nutrition: NutritionInfo
    per_serving_nutrition: NutritionInfo
    health_score: float
    recommendations: List[str]


class BMICalculationRequest(BaseModel):
    """Schema for BMI calculation request."""
    
    weight: float = Field(..., ge=30, le=100, description="Waga (kg)")
    height: float = Field(..., ge=120, le=200, description="Wzrost (cm)")
    age: int = Field(..., ge=10, le=18, description="Wiek")


class BMICalculationResponse(BaseModel):
    """Schema for BMI calculation response."""
    
    bmi: float
    bmi_category: str
    healthy_weight_range: Dict[str, float]
    recommendations: List[str]


class CookingChallengeRequest(BaseModel):
    """Schema for cooking challenge request."""
    
    difficulty: str = Field(..., description="Poziom trudności")
    cuisine_type: Optional[str] = Field(None, description="Typ kuchni")
    available_ingredients: Optional[List[str]] = Field(None, description="Dostępne składniki")
    time_limit: Optional[int] = Field(None, ge=0, description="Limit czasu w minutach")


class CookingChallengeResponse(BaseModel):
    """Schema for cooking challenge response."""
    
    challenge_id: int
    title: str
    description: str
    difficulty: str
    ingredients: List[str]
    instructions: List[str]
    time_limit: int
    points_reward: int
    tips: List[str]


class WeeklyMealPlanRequest(BaseModel):
    """Schema for weekly meal plan request."""
    
    start_date: str = Field(..., description="Data rozpoczęcia (YYYY-MM-DD)")
    preferences: Optional[str] = Field(None, description="Preferencje")
    budget: Optional[float] = Field(None, ge=0, description="Budżet tygodniowy")


class WeeklyMealPlanResponse(BaseModel):
    """Schema for weekly meal plan response."""
    
    week_start: str
    total_cost: float
    daily_plans: List[Dict[str, Any]]
    shopping_list: List[Dict[str, Any]]
    nutrition_summary: Dict[str, Any]


class ProductCategoryRequest(BaseModel):
    """Schema for product category management."""
    
    name: str = Field(..., min_length=1, max_length=50, description="Nazwa kategorii")
    description: Optional[str] = Field(None, description="Opis kategorii")
    color: Optional[str] = Field(None, description="Kolor kategorii")
    icon: Optional[str] = Field(None, description="Ikona kategorii")


class ProductCategoryResponse(BaseModel):
    """Schema for product category response."""
    
    id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    product_count: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class CookingAchievementRequest(BaseModel):
    """Schema for cooking achievement request."""
    
    achievement_type: str = Field(..., description="Typ osiągnięcia")
    recipe_id: Optional[int] = Field(None, description="ID przepisu")
    description: Optional[str] = Field(None, description="Opis osiągnięcia")


class CookingAchievementResponse(BaseModel):
    """Schema for cooking achievement response."""
    
    id: int
    user_id: int
    achievement_type: str
    title: str
    description: str
    points_earned: int
    icon: str
    unlocked_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    ) 