"""
Cooking service for Ageny Online.
Zapewnia logikę biznesową dla funkcjonalności kulinarnych.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

from backend.models import Product, Recipe, ShoppingList
from backend.schemas.cooking import (
    ProductCreate, ProductUpdate,
    RecipeCreate, RecipeUpdate,
    ShoppingListCreate, ShoppingListUpdate
)
from backend.exceptions.database import ValidationError

logger = logging.getLogger(__name__)


class CookingProductService:
    """Service for product management operations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_product(self, product_data: ProductCreate, user_id: int) -> Product:
        """Add a new product.

        Args:
            product_data: Product creation data
            user_id: User ID

        Returns:
            Created product instance

        Raises:
            ValidationError: If product creation fails
        """
        try:
            # Check if product already exists for this user
            existing_product = await self.get_product_by_name(product_data.name, user_id)
            if existing_product:
                raise ValidationError(f"Product '{product_data.name}' already exists")

            # Create product
            product = Product(
                name=product_data.name,
                category=product_data.category,
                unit=product_data.unit,
                price_per_unit=product_data.price_per_unit,
                calories_per_100g=product_data.calories_per_100g,
                proteins=product_data.proteins,
                carbs=product_data.carbs,
                fats=product_data.fats,
                user_id=user_id
            )

            self.db_session.add(product)
            await self.db_session.commit()
            await self.db_session.refresh(product)

            logger.info(f"Product created successfully: {product.name} for user {user_id}")
            return product

        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to create product: {e}")

    async def list_products(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of product instances
        """
        result = await self.db_session.execute(
            select(Product)
            .where(Product.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Product.name)
        )
        return result.scalars().all()

    async def get_product_by_id(self, product_id: int, user_id: int) -> Optional[Product]:
        """Get product by ID.

        Args:
            product_id: Product ID
            user_id: User ID

        Returns:
            Product instance or None
        """
        result = await self.db_session.execute(
            select(Product).where(
                and_(Product.id == product_id, Product.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_product_by_name(self, name: str, user_id: int) -> Optional[Product]:
        """Get product by name.

        Args:
            name: Product name
            user_id: User ID

        Returns:
            Product instance or None
        """
        result = await self.db_session.execute(
            select(Product).where(
                and_(Product.name == name, Product.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def update_product(self, product_id: int, product_data: ProductUpdate, user_id: int) -> Optional[Product]:
        """Update product data.

        Args:
            product_id: Product ID
            product_data: Product update data
            user_id: User ID

        Returns:
            Updated product instance or None

        Raises:
            ValidationError: If update fails
        """
        try:
            product = await self.get_product_by_id(product_id, user_id)
            if not product:
                return None

            # Update fields
            for field, value in product_data.dict(exclude_unset=True).items():
                setattr(product, field, value)

            product.updated_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(product)

            logger.info(f"Product updated successfully: {product.name}")
            return product

        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to update product: {e}")

    async def delete_product(self, product_id: int, user_id: int) -> bool:
        """Delete product.

        Args:
            product_id: Product ID
            user_id: User ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValidationError: If deletion fails
        """
        try:
            product = await self.get_product_by_id(product_id, user_id)
            if not product:
                return False

            await self.db_session.delete(product)
            await self.db_session.commit()

            logger.info(f"Product deleted successfully: {product.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to delete product: {e}")

    async def search_products(self, query: str, user_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name or category.

        Args:
            query: Search query
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching product instances
        """
        result = await self.db_session.execute(
            select(Product)
            .where(
                and_(
                    Product.user_id == user_id,
                    or_(
                        Product.name.ilike(f"%{query}%"),
                        Product.category.ilike(f"%{query}%")
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Product.name)
        )
        return result.scalars().all()

    async def list_categories(self, user_id: int) -> List[str]:
        """List unique product categories for a user.

        Args:
            user_id: User ID

        Returns:
            List of unique category names
        """
        result = await self.db_session.execute(
            select(Product.category)
            .where(Product.user_id == user_id)
            .distinct()
            .order_by(Product.category)
        )
        return [row[0] for row in result.all()]


class CookingRecipeService:
    """Service for recipe management operations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def generate_recipe(self, ingredients: list, preferences: str, user_id: int):
        """Generate recipe using AI.

        Args:
            ingredients: List of available ingredients
            preferences: User preferences
            user_id: User ID

        Returns:
            Generated recipe data
        """
        try:
            from backend.core.llm_providers.provider_factory import provider_factory
            
            # Create AI prompt for recipe generation
            prompt = f"""
            Stwórz przepis kulinarny używając następujących składników: {', '.join(ingredients)}
            
            Preferencje: {preferences}
            
            Odpowiedz w formacie JSON:
            {{
                "name": "Nazwa przepisu",
                "description": "Krótki opis",
                "ingredients": [{{"name": "nazwa", "amount": "ilość", "unit": "jednostka"}}],
                "instructions": "Kroki przygotowania",
                "cooking_time": 30,
                "difficulty": "łatwy",
                "servings": 4,
                "calories_per_serving": 250,
                "tags": ["kuchnia polska", "wegetariańska"]
            }}
            """
            
            # Generate recipe using LLM
            result = await provider_factory.chat_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # Parse JSON response
            import json
            recipe_data = json.loads(result["text"])
            
            logger.info(f"Recipe generated successfully for user {user_id}")
            return recipe_data
            
        except Exception as e:
            logger.error(f"Failed to generate recipe: {e}")
            # Return fallback recipe
            return {
                "name": f"Przepis z {', '.join(ingredients[:3])}",
                "description": f"Przepis przygotowany z dostępnych składników: {', '.join(ingredients)}",
                "ingredients": [{"name": ing, "amount": "1", "unit": "szt"} for ing in ingredients],
                "instructions": "Wymieszaj wszystkie składniki i dopraw do smaku.",
                "cooking_time": 15,
                "difficulty": "łatwy",
                "servings": 2,
                "calories_per_serving": 200,
                "tags": ["szybki", "prosty"]
            }

    async def save_recipe(self, recipe_data: RecipeCreate, user_id: int) -> Recipe:
        """Save a new recipe.

        Args:
            recipe_data: Recipe creation data
            user_id: User ID

        Returns:
            Created recipe instance

        Raises:
            ValidationError: If recipe creation fails
        """
        try:
            # Check if recipe already exists for this user
            existing_recipe = await self.get_recipe_by_name(recipe_data.name, user_id)
            if existing_recipe:
                raise ValidationError(f"Recipe '{recipe_data.name}' already exists")

            # Create recipe
            recipe = Recipe(
                name=recipe_data.name,
                description=recipe_data.description,
                ingredients=recipe_data.ingredients,
                instructions=recipe_data.instructions,
                cooking_time=recipe_data.cooking_time,
                difficulty=recipe_data.difficulty,
                servings=recipe_data.servings,
                calories_per_serving=recipe_data.calories_per_serving,
                tags=recipe_data.tags,
                user_id=user_id,
                is_ai_generated=False
            )

            self.db_session.add(recipe)
            await self.db_session.commit()
            await self.db_session.refresh(recipe)

            logger.info(f"Recipe created successfully: {recipe.name} for user {user_id}")
            return recipe

        except Exception as e:
            logger.error(f"Failed to create recipe: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to create recipe: {e}")

    async def list_recipes(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """List recipes for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of recipe instances
        """
        result = await self.db_session.execute(
            select(Recipe)
            .where(Recipe.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Recipe.name)
        )
        return result.scalars().all()

    async def get_recipe(self, recipe_id: int, user_id: int) -> Optional[Recipe]:
        """Get recipe by ID.

        Args:
            recipe_id: Recipe ID
            user_id: User ID

        Returns:
            Recipe instance or None
        """
        result = await self.db_session.execute(
            select(Recipe).where(
                and_(Recipe.id == recipe_id, Recipe.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_recipe_by_name(self, name: str, user_id: int) -> Optional[Recipe]:
        """Get recipe by name.

        Args:
            name: Recipe name
            user_id: User ID

        Returns:
            Recipe instance or None
        """
        result = await self.db_session.execute(
            select(Recipe).where(
                and_(Recipe.name == name, Recipe.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def update_recipe(self, recipe_id: int, recipe_data: RecipeUpdate, user_id: int) -> Optional[Recipe]:
        """Update recipe data.

        Args:
            recipe_id: Recipe ID
            recipe_data: Recipe update data
            user_id: User ID

        Returns:
            Updated recipe instance or None

        Raises:
            ValidationError: If update fails
        """
        try:
            recipe = await self.get_recipe(recipe_id, user_id)
            if not recipe:
                return None

            # Update fields
            for field, value in recipe_data.dict(exclude_unset=True).items():
                setattr(recipe, field, value)

            recipe.updated_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(recipe)

            logger.info(f"Recipe updated successfully: {recipe.name}")
            return recipe

        except Exception as e:
            logger.error(f"Failed to update recipe {recipe_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to update recipe: {e}")

    async def delete_recipe(self, recipe_id: int, user_id: int) -> bool:
        """Delete recipe.

        Args:
            recipe_id: Recipe ID
            user_id: User ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValidationError: If deletion fails
        """
        try:
            recipe = await self.get_recipe(recipe_id, user_id)
            if not recipe:
                return False

            await self.db_session.delete(recipe)
            await self.db_session.commit()

            logger.info(f"Recipe deleted successfully: {recipe.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete recipe {recipe_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to delete recipe: {e}")

    async def search_recipes(self, query: str, user_id: int, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """Search recipes by name, description, or tags.

        Args:
            query: Search query
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching recipe instances
        """
        result = await self.db_session.execute(
            select(Recipe)
            .where(
                and_(
                    Recipe.user_id == user_id,
                    or_(
                        Recipe.name.ilike(f"%{query}%"),
                        Recipe.description.ilike(f"%{query}%")
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Recipe.name)
        )
        return result.scalars().all()


class CookingShoppingListService:
    """Service for shopping list management operations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_shopping_list(self, shopping_list_data: ShoppingListCreate, user_id: int) -> ShoppingList:
        """Create a new shopping list.

        Args:
            shopping_list_data: Shopping list creation data
            user_id: User ID

        Returns:
            Created shopping list instance

        Raises:
            ValidationError: If shopping list creation fails
        """
        try:
            # Check if shopping list with same name already exists for this user
            existing_list = await self.get_shopping_list_by_name(shopping_list_data.name, user_id)
            if existing_list:
                raise ValidationError(f"Shopping list '{shopping_list_data.name}' already exists")

            # Calculate estimated cost if budget is provided
            total_estimated_cost = None
            if shopping_list_data.budget:
                total_estimated_cost = await self._calculate_list_cost(shopping_list_data.items, user_id)

            # Create shopping list
            shopping_list = ShoppingList(
                name=shopping_list_data.name,
                items=shopping_list_data.items,
                total_estimated_cost=total_estimated_cost,
                user_id=user_id
            )

            self.db_session.add(shopping_list)
            await self.db_session.commit()
            await self.db_session.refresh(shopping_list)

            logger.info(f"Shopping list created successfully: {shopping_list.name} for user {user_id}")
            return shopping_list

        except Exception as e:
            logger.error(f"Failed to create shopping list: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to create shopping list: {e}")

    async def list_shopping_lists(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShoppingList]:
        """List shopping lists for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of shopping list instances
        """
        result = await self.db_session.execute(
            select(ShoppingList)
            .where(ShoppingList.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(ShoppingList.created_at.desc())
        )
        return result.scalars().all()

    async def get_shopping_list(self, list_id: int, user_id: int) -> Optional[ShoppingList]:
        """Get shopping list by ID.

        Args:
            list_id: Shopping list ID
            user_id: User ID

        Returns:
            Shopping list instance or None
        """
        result = await self.db_session.execute(
            select(ShoppingList).where(
                and_(ShoppingList.id == list_id, ShoppingList.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_shopping_list_by_name(self, name: str, user_id: int) -> Optional[ShoppingList]:
        """Get shopping list by name.

        Args:
            name: Shopping list name
            user_id: User ID

        Returns:
            Shopping list instance or None
        """
        result = await self.db_session.execute(
            select(ShoppingList).where(
                and_(ShoppingList.name == name, ShoppingList.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def complete_shopping_list(self, list_id: int, user_id: int) -> Optional[ShoppingList]:
        """Mark shopping list as completed.

        Args:
            list_id: Shopping list ID
            user_id: User ID

        Returns:
            Updated shopping list instance or None

        Raises:
            ValidationError: If update fails
        """
        try:
            shopping_list = await self.get_shopping_list(list_id, user_id)
            if not shopping_list:
                return None

            shopping_list.is_completed = True
            shopping_list.updated_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(shopping_list)

            logger.info(f"Shopping list completed: {shopping_list.name}")
            return shopping_list

        except Exception as e:
            logger.error(f"Failed to complete shopping list {list_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to complete shopping list: {e}")

    async def delete_shopping_list(self, list_id: int, user_id: int) -> bool:
        """Delete shopping list.

        Args:
            list_id: Shopping list ID
            user_id: User ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValidationError: If deletion fails
        """
        try:
            shopping_list = await self.get_shopping_list(list_id, user_id)
            if not shopping_list:
                return False

            await self.db_session.delete(shopping_list)
            await self.db_session.commit()

            logger.info(f"Shopping list deleted successfully: {shopping_list.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete shopping list {list_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to delete shopping list: {e}")

    async def estimate_cost(self, list_id: int, user_id: int) -> float:
        """Estimate total cost of shopping list.

        Args:
            list_id: Shopping list ID
            user_id: User ID

        Returns:
            Estimated total cost
        """
        shopping_list = await self.get_shopping_list(list_id, user_id)
        if not shopping_list:
            return 0.0

        return await self._calculate_list_cost(shopping_list.items, user_id)

    async def optimize_shopping_list(self, items: List[dict], budget: float, preferences: str, user_id: int) -> dict:
        """Optimize shopping list using AI.

        Args:
            items: List of shopping items
            budget: Available budget
            preferences: User preferences
            user_id: User ID

        Returns:
            Optimized shopping list data
        """
        try:
            from backend.core.llm_providers.provider_factory import provider_factory
            
            # Create AI prompt for shopping list optimization
            prompt = f"""
            Zoptymalizuj listę zakupów:
            Produkty: {items}
            Budżet: {budget} zł
            Preferencje: {preferences}
            
            Uwzględnij:
            - Najlepsze ceny
            - Sezonowość produktów
            - Zamienniki tańsze
            - Minimalizację odpadów
            - Promocje i zniżki
            
            Odpowiedz w formacie JSON:
            {{
                "optimized_items": [{{"product_name": "nazwa", "quantity": 1, "unit": "szt", "estimated_price": 5.0}}],
                "total_cost": 25.0,
                "savings": 5.0,
                "recommendations": ["Zalecenia optymalizacji"]
            }}
            """
            
            # Generate optimization using LLM
            result = await provider_factory.chat_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            # Parse JSON response
            import json
            optimization_data = json.loads(result["text"])
            
            logger.info(f"Shopping list optimized successfully for user {user_id}")
            return optimization_data
            
        except Exception as e:
            logger.error(f"Failed to optimize shopping list: {e}")
            # Return fallback optimization
            total_cost = sum(item.get('estimated_price', 0) for item in items)
            return {
                "optimized_items": items,
                "total_cost": total_cost,
                "savings": 0.0,
                "recommendations": ["Nie udało się zoptymalizować listy"]
            }

    async def _calculate_list_cost(self, items: List[dict], user_id: int) -> float:
        """Calculate total cost for list of items.

        Args:
            items: List of shopping items
            user_id: User ID

        Returns:
            Total estimated cost
        """
        total_cost = 0.0
        
        for item in items:
            product_name = item.get('product_name', '')
            quantity = item.get('quantity', 0)
            
            # Try to find product in user's database
            product_service = CookingProductService(self.db_session)
            product = await product_service.get_product_by_name(product_name, user_id)
            
            if product and product.price_per_unit:
                total_cost += product.price_per_unit * quantity
            else:
                # Use estimated price from item if available
                estimated_price = item.get('estimated_price', 0)
                total_cost += estimated_price

        return total_cost 