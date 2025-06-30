"""
Cooking endpoints for Ageny Online.
Zapewnia API dla funkcjonalności kulinarnych z pełną separacją.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from backend.database import get_async_session
from backend.services.cooking_service import (
    CookingProductService, CookingRecipeService, CookingShoppingListService
)
from backend.services.ocr_service import OCRService
from backend.schemas.cooking import (
    ProductCreate, ProductResponse, ProductUpdate, ProductSearchRequest,
    RecipeCreate, RecipeResponse, RecipeUpdate, RecipeSearchRequest,
    ShoppingListCreate, ShoppingListResponse, ShoppingListUpdate,
    RecipeGenerationRequest, ShoppingListOptimizationRequest,
    CookingStatsResponse, MealPlanRequest, MealPlanResponse,
    RecipeNutritionRequest, RecipeNutritionResponse, BMICalculationRequest,
    BMICalculationResponse, CookingChallengeRequest, CookingChallengeResponse,
    WeeklyMealPlanRequest, WeeklyMealPlanResponse, ProductCategoryRequest,
    ProductCategoryResponse, CookingAchievementRequest, CookingAchievementResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Cooking"])


# --- Produkty ---
@router.post("/products/add", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Add a new product."""
    try:
        service = CookingProductService(db)
        result = await service.add_product(product, user_id)
        return ProductResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to add product: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products/list", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """List products for a user."""
    try:
        service = CookingProductService(db)
        products = await service.list_products(user_id, skip=skip, limit=limit)
        return [ProductResponse.from_orm(product) for product in products]
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/categories", response_model=List[str])
async def list_product_categories(
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """List unique product categories for a user."""
    try:
        service = CookingProductService(db)
        categories = await service.list_categories(user_id)
        return categories
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Update a product."""
    try:
        service = CookingProductService(db)
        result = await service.update_product(product_id, product, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update product: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Delete a product."""
    try:
        service = CookingProductService(db)
        deleted = await service.delete_product(product_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Product not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete product: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/products/scan", response_model=List[ProductResponse])
async def scan_product(
    image: UploadFile = File(..., description="Image of product to scan"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Scan product using OCR and AI to extract product information."""
    try:
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await image.read()
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # OCR Service to extract text
        ocr_service = OCRService(db)
        
        # Custom prompt for product scanning
        product_prompt = """
        Analyze this image and extract product information. Look for:
        - Product name
        - Brand name
        - Nutritional information (calories, proteins, carbs, fats per 100g)
        - Weight/volume
        - Price (if visible)
        
        Return the information in a structured format.
        """
        
        # Extract text using OCR
        ocr_result = await ocr_service.extract_text(
            image_bytes=image_bytes,
            user_id=user_id,
            session_id=f"product_scan_{user_id}",
            prompt=product_prompt
        )
        
        # Cooking Service to process OCR result and create products
        cooking_service = CookingProductService(db)
        
        # Use AI to parse OCR text and create product
        # This is a simplified version - in production you'd use more sophisticated parsing
        extracted_text = ocr_result["text"]
        
        # Try to extract product information from OCR text
        # For now, we'll create a basic product and let user edit it
        product_create = ProductCreate(
            name=f"Scanned Product - {extracted_text[:50]}...",
            category="scanned",
            unit="szt",
            price_per_unit=0.0,
            calories_per_100g=0,
            proteins=0.0,
            carbs=0.0,
            fats=0.0
        )
        
        # Save the scanned product
        result = await cooking_service.add_product(product_create, user_id)
        
        logger.info(f"Product scanned successfully for user {user_id}: {result.name}")
        
        return [ProductResponse.from_orm(result)]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scan product: {e}")
        raise HTTPException(status_code=500, detail=f"Product scanning failed: {str(e)}")


@router.get("/products/search", response_model=List[ProductResponse])
async def search_products(
    query: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Search products by name or category."""
    try:
        service = CookingProductService(db)
        products = await service.search_products(query, user_id, skip=skip, limit=limit)
        return [ProductResponse.from_orm(product) for product in products]
    except Exception as e:
        logger.error(f"Failed to search products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Przepisy ---
@router.post("/recipes/generate", response_model=RecipeResponse)
async def generate_recipe(
    request: RecipeGenerationRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Generate a recipe using AI based on available ingredients."""
    try:
        service = CookingRecipeService(db)
        result = await service.generate_recipe(request, user_id)
        return RecipeResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to generate recipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recipes/save", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def save_recipe(
    recipe: RecipeCreate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Save a new recipe."""
    try:
        service = CookingRecipeService(db)
        result = await service.add_recipe(recipe, user_id)
        return RecipeResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to save recipe: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recipes/list", response_model=List[RecipeResponse])
async def list_recipes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """List recipes for a user."""
    try:
        service = CookingRecipeService(db)
        recipes = await service.list_recipes(user_id, skip=skip, limit=limit)
        return [RecipeResponse.from_orm(recipe) for recipe in recipes]
    except Exception as e:
        logger.error(f"Failed to list recipes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Get a specific recipe."""
    try:
        service = CookingRecipeService(db)
        recipe = await service.get_recipe(recipe_id, user_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return RecipeResponse.from_orm(recipe)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recipes/search", response_model=List[RecipeResponse])
async def search_recipes(
    query: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Search recipes by name, ingredients, or tags."""
    try:
        service = CookingRecipeService(db)
        recipes = await service.search_recipes(query, user_id, skip=skip, limit=limit)
        return [RecipeResponse.from_orm(recipe) for recipe in recipes]
    except Exception as e:
        logger.error(f"Failed to search recipes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recipes/from-ingredients", response_model=RecipeResponse)
async def recipe_from_ingredients(
    request: RecipeGenerationRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Generate a recipe from available ingredients."""
    try:
        service = CookingRecipeService(db)
        result = await service.generate_recipe_from_ingredients(request, user_id)
        return RecipeResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to generate recipe from ingredients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recipes/optimize", response_model=RecipeResponse)
async def optimize_recipe(
    recipe_id: int = Query(..., description="Recipe ID to optimize"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Optimize a recipe using AI."""
    try:
        service = CookingRecipeService(db)
        result = await service.optimize_recipe(recipe_id, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return RecipeResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize recipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Delete a recipe."""
    try:
        service = CookingRecipeService(db)
        deleted = await service.delete_recipe(recipe_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Recipe not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete recipe: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# --- Lista zakupów ---
@router.post("/shopping/create", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    shopping_list: ShoppingListCreate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Create a new shopping list."""
    try:
        service = CookingShoppingListService(db)
        result = await service.create_shopping_list(shopping_list, user_id)
        return ShoppingListResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to create shopping list: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/shopping/from-recipe", response_model=ShoppingListResponse)
async def shopping_list_from_recipe(
    recipe_id: int = Query(..., description="Recipe ID"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Create a shopping list from a recipe."""
    try:
        service = CookingShoppingListService(db)
        result = await service.create_shopping_list_from_recipe(recipe_id, user_id)
        return ShoppingListResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to create shopping list from recipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shopping/optimize", response_model=ShoppingListResponse)
async def optimize_shopping_list(
    request: ShoppingListOptimizationRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Optimize a shopping list using AI."""
    try:
        service = CookingShoppingListService(db)
        result = await service.optimize_shopping_list(request, user_id)
        return ShoppingListResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to optimize shopping list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shopping/list", response_model=List[ShoppingListResponse])
async def list_shopping_lists(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """List shopping lists for a user."""
    try:
        service = CookingShoppingListService(db)
        shopping_lists = await service.list_shopping_lists(user_id, skip=skip, limit=limit)
        return [ShoppingListResponse.from_orm(shopping_list) for shopping_list in shopping_lists]
    except Exception as e:
        logger.error(f"Failed to list shopping lists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/shopping/{list_id}/complete", response_model=ShoppingListResponse)
async def complete_shopping_list(
    list_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Mark a shopping list as completed."""
    try:
        service = CookingShoppingListService(db)
        result = await service.complete_shopping_list(list_id, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        return ShoppingListResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete shopping list: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/shopping/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Delete a shopping list."""
    try:
        service = CookingShoppingListService(db)
        deleted = await service.delete_shopping_list(list_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Shopping list not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete shopping list: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/shopping/{list_id}/cost", response_model=float)
async def estimate_shopping_list_cost(
    list_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Estimate the cost of a shopping list."""
    try:
        service = CookingShoppingListService(db)
        cost = await service.estimate_shopping_list_cost(list_id, user_id)
        return cost
    except Exception as e:
        logger.error(f"Failed to estimate shopping list cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- NEW: Extended endpoints for Antonina's cooking features ---

@router.get("/stats", response_model=CookingStatsResponse)
async def get_cooking_stats(
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")
):
    """Get cooking statistics for Antonina."""
    try:
        product_service = CookingProductService(db)
        recipe_service = CookingRecipeService(db)
        shopping_service = CookingShoppingListService(db)
        
        # Get basic stats
        total_products = await product_service.count_products(user_id)
        total_recipes = await recipe_service.count_recipes(user_id)
        total_shopping_lists = await shopping_service.count_shopping_lists(user_id)
        completed_shopping_lists = await shopping_service.count_completed_shopping_lists(user_id)
        
        # Get favorite categories
        categories = await product_service.list_categories(user_id)
        
        # Get recent items
        recent_recipes = await recipe_service.get_recent_recipes(user_id, limit=5)
        recent_shopping_lists = await shopping_service.get_recent_shopping_lists(user_id, limit=5)
        
        # Calculate total spent (simplified)
        total_spent = 0.0  # TODO: Implement actual spending calculation
        
        return CookingStatsResponse(
            total_products=total_products,
            total_recipes=total_recipes,
            total_shopping_lists=total_shopping_lists,
            completed_shopping_lists=completed_shopping_lists,
            total_spent=total_spent,
            favorite_categories=categories[:5],  # Top 5 categories
            recent_recipes=[{"id": r.id, "name": r.name, "created_at": r.created_at} for r in recent_recipes],
            recent_shopping_lists=[{"id": sl.id, "name": sl.name, "created_at": sl.created_at} for sl in recent_shopping_lists]
        )
    except Exception as e:
        logger.error(f"Failed to get cooking stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meal-plan", response_model=MealPlanResponse)
async def create_meal_plan(
    request: MealPlanRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")
):
    """Create a personalized meal plan for Antonina."""
    try:
        # Import diet plugin functionality
        from backend.plugins.diet_plugin import diet_plugin
        return await diet_plugin._generate_meal_plan(request, db, user_id)
    except Exception as e:
        logger.error(f"Failed to create meal plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bmi", response_model=BMICalculationResponse)
async def calculate_bmi(request: BMICalculationRequest):
    """Calculate BMI and provide recommendations for Antonina."""
    try:
        from backend.plugins.diet_plugin import diet_plugin
        return await diet_plugin._calculate_bmi(request)
    except Exception as e:
        logger.error(f"Failed to calculate BMI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recipe-nutrition", response_model=RecipeNutritionResponse)
async def analyze_recipe_nutrition(
    request: RecipeNutritionRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")
):
    """Analyze nutrition value of a recipe."""
    try:
        from backend.plugins.diet_plugin import diet_plugin
        return await diet_plugin._analyze_recipe_nutrition(request, db, user_id)
    except Exception as e:
        logger.error(f"Failed to analyze recipe nutrition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/challenges", response_model=CookingChallengeResponse)
async def create_cooking_challenge(
    request: CookingChallengeRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")
):
    """Create a cooking challenge for Antonina."""
    try:
        # Generate cooking challenge using AI
        from backend.core.llm_providers.provider_factory import provider_factory
        
        prompt = f"""
        Stwórz wyzwanie kulinarne dla 14-letniej dziewczynki:
        
        Poziom trudności: {request.difficulty}
        Typ kuchni: {request.cuisine_type or 'dowolny'}
        Dostępne składniki: {', '.join(request.available_ingredients) if request.available_ingredients else 'dowolne'}
        Limit czasu: {request.time_limit or 60} minut
        
        Stwórz:
        - Tytuł wyzwania
        - Opis
        - Listę składników
        - Instrukcje krok po kroku
        - Wskazówki
        - Punkty do zdobycia
        
        Odpowiedz w formacie JSON.
        """
        
        response = await provider_factory.chat_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        
        # Simplified response for now
        return CookingChallengeResponse(
            challenge_id=1,
            title=f"Wyzwanie: {request.cuisine_type or 'Kulinarne'}",
            description="Przygotuj pyszne danie w określonym czasie!",
            difficulty=request.difficulty,
            ingredients=["składnik 1", "składnik 2", "składnik 3"],
            instructions=["Krok 1", "Krok 2", "Krok 3"],
            time_limit=request.time_limit or 60,
            points_reward=100,
            tips=["Wskazówka 1", "Wskazówka 2"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create cooking challenge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weekly-plan", response_model=WeeklyMealPlanResponse)
async def create_weekly_meal_plan(
    request: WeeklyMealPlanRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")
):
    """Create a weekly meal plan for Antonina."""
    try:
        # Generate weekly meal plan
        from backend.core.llm_providers.provider_factory import provider_factory
        
        prompt = f"""
        Stwórz tygodniowy plan posiłków dla 14-letniej dziewczynki:
        
        Data rozpoczęcia: {request.start_date}
        Preferencje: {request.preferences or 'brak'}
        Budżet tygodniowy: {request.budget or 'nieograniczony'} PLN
        
        Stwórz plan na 7 dni z:
        - Śniadaniem
        - Drugim śniadaniem
        - Obiadem
        - Podwieczorkiem
        - Kolacją
        
        Każdy posiłek powinien zawierać:
        - Nazwę
        - Składniki
        - Kalorie
        - Koszt
        
        Odpowiedz w formacie JSON.
        """
        
        response = await provider_factory.chat_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Simplified response for now
        return WeeklyMealPlanResponse(
            week_start=request.start_date,
            total_cost=request.budget or 200.0,
            daily_plans=[
                {
                    "day": "Poniedziałek",
                    "meals": [
                        {"name": "Śniadanie", "calories": 300},
                        {"name": "Obiad", "calories": 500}
                    ]
                }
            ],
            shopping_list=[],
            nutrition_summary={
                "total_calories": 2000,
                "total_proteins": 80,
                "total_carbs": 250,
                "total_fats": 70
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create weekly meal plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_product_category(
    category: ProductCategoryRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")
):
    """Create a new product category for Antonina."""
    try:
        # TODO: Implement category service
        return ProductCategoryResponse(
            id=1,
            name=category.name,
            description=category.description,
            color=category.color,
            icon=category.icon,
            product_count=0,
            created_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Failed to create product category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nutrition-tips")
async def get_nutrition_tips():
    """Get nutrition tips for teenagers."""
    try:
        from backend.plugins.diet_plugin import diet_plugin
        return await diet_plugin.get_nutrition_tips()
    except Exception as e:
        logger.error(f"Failed to get nutrition tips: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 