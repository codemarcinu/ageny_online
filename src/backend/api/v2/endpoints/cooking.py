"""
Cooking endpoints for Ageny Online.
Zapewnia API dla funkcjonalności kulinarnych z pełną separacją.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.database import get_async_session
from backend.services.cooking_service import (
    CookingProductService, CookingRecipeService, CookingShoppingListService
)
from backend.services.ocr_service import OCRService
from backend.schemas.cooking import (
    ProductCreate, ProductResponse, ProductUpdate, ProductSearchRequest,
    RecipeCreate, RecipeResponse, RecipeUpdate, RecipeSearchRequest,
    ShoppingListCreate, ShoppingListResponse, ShoppingListUpdate,
    RecipeGenerationRequest, ShoppingListOptimizationRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cooking", tags=["Cooking"])


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
    """Generate recipe using AI."""
    try:
        service = CookingRecipeService(db)
        recipe_data = await service.generate_recipe(
            request.ingredients, request.preferences, user_id
        )
        
        # Create recipe from generated data
        recipe_create = RecipeCreate(
            name=recipe_data["name"],
            ingredients=recipe_data["ingredients"],
            instructions=recipe_data["instructions"],
            is_ai_generated=True
        )
        
        result = await service.save_recipe(recipe_create, user_id)
        return RecipeResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to generate recipe: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recipes/save", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def save_recipe(
    recipe: RecipeCreate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Save a new recipe."""
    try:
        service = CookingRecipeService(db)
        result = await service.save_recipe(recipe, user_id)
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
    """Search recipes by name or description."""
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
    """Generate recipe from available ingredients."""
    try:
        service = CookingRecipeService(db)
        recipe_data = await service.generate_recipe(
            request.ingredients, request.preferences, user_id
        )
        
        # Create recipe from generated data
        recipe_create = RecipeCreate(
            name=recipe_data["name"],
            ingredients=recipe_data["ingredients"],
            instructions=recipe_data["instructions"],
            is_ai_generated=True
        )
        
        result = await service.save_recipe(recipe_create, user_id)
        return RecipeResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Failed to generate recipe from ingredients: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recipes/optimize", response_model=RecipeResponse)
async def optimize_recipe(
    recipe_id: int = Query(..., description="Recipe ID to optimize"),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Optimize recipe using AI (placeholder)."""
    # TODO: Implement AI recipe optimization
    logger.info(f"Recipe optimization requested for recipe {recipe_id} by user {user_id}")
    raise HTTPException(status_code=501, detail="Recipe optimization not implemented yet")


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


# --- Listy zakupów ---
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
    """Create shopping list from recipe ingredients (placeholder)."""
    # TODO: Implement shopping list creation from recipe
    logger.info(f"Shopping list from recipe requested for recipe {recipe_id} by user {user_id}")
    raise HTTPException(status_code=501, detail="Shopping list from recipe not implemented yet")


@router.post("/shopping/optimize", response_model=ShoppingListResponse)
async def optimize_shopping_list(
    request: ShoppingListOptimizationRequest,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Query(..., description="User ID")  # TODO: Replace with proper auth
):
    """Optimize shopping list using AI (placeholder)."""
    # TODO: Implement AI shopping list optimization
    logger.info(f"Shopping list optimization requested for user {user_id}")
    raise HTTPException(status_code=501, detail="Shopping list optimization not implemented yet")


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
    """Mark shopping list as completed."""
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
    """Estimate total cost of shopping list."""
    try:
        service = CookingShoppingListService(db)
        cost = await service.estimate_cost(list_id, user_id)
        return cost
    except Exception as e:
        logger.error(f"Failed to estimate shopping list cost: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 