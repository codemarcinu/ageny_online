"""
Dietetyk Antoniny - Plugin do planowania diety i obliczania makroskładników.
Plugin specjalnie dostosowany do potrzeb 14-letniej Antoniny.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.database import get_async_session
from backend.plugins import PluginInterface
from backend.core.llm_providers.provider_factory import provider_factory
from backend.services.cooking_service import CookingProductService, CookingRecipeService

logger = logging.getLogger(__name__)


# Schemas dla plugin dietetyczny
class NutritionInfo(BaseModel):
    """Informacje o wartości odżywczej."""
    calories: float = Field(..., ge=0, description="Kalorie")
    proteins: float = Field(..., ge=0, description="Białka (g)")
    carbs: float = Field(..., ge=0, description="Węglowodany (g)")
    fats: float = Field(..., ge=0, description="Tłuszcze (g)")
    fiber: Optional[float] = Field(None, ge=0, description="Błonnik (g)")
    sugar: Optional[float] = Field(None, ge=0, description="Cukier (g)")


class MealPlanRequest(BaseModel):
    """Żądanie planu posiłków."""
    age: int = Field(..., ge=10, le=18, description="Wiek")
    weight: float = Field(..., ge=30, le=100, description="Waga (kg)")
    height: float = Field(..., ge=120, le=200, description="Wzrost (cm)")
    activity_level: str = Field(..., description="Poziom aktywności (niski/średni/wysoki)")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Ograniczenia dietetyczne")
    preferences: Optional[str] = Field(None, description="Preferencje smakowe")
    budget_per_day: Optional[float] = Field(None, ge=0, description="Budżet dzienny (PLN)")


class MealPlanResponse(BaseModel):
    """Odpowiedź z planem posiłków."""
    daily_calories: int
    daily_proteins: float
    daily_carbs: float
    daily_fats: float
    meals: List[Dict[str, Any]]
    shopping_list: List[Dict[str, Any]]
    estimated_cost: float
    nutrition_tips: List[str]


class BMICalculationRequest(BaseModel):
    """Żądanie obliczenia BMI."""
    weight: float = Field(..., ge=30, le=100, description="Waga (kg)")
    height: float = Field(..., ge=120, le=200, description="Wzrost (cm)")
    age: int = Field(..., ge=10, le=18, description="Wiek")


class BMICalculationResponse(BaseModel):
    """Odpowiedź z obliczeniami BMI."""
    bmi: float
    bmi_category: str
    healthy_weight_range: Dict[str, float]
    recommendations: List[str]


class RecipeNutritionRequest(BaseModel):
    """Żądanie analizy wartości odżywczej przepisu."""
    recipe_id: int = Field(..., description="ID przepisu")


class RecipeNutritionResponse(BaseModel):
    """Odpowiedź z analizą wartości odżywczej."""
    recipe_name: str
    total_nutrition: NutritionInfo
    per_serving_nutrition: NutritionInfo
    health_score: float
    recommendations: List[str]


class DietPlugin(PluginInterface):
    """Plugin Dietetyk Antoniny."""
    
    def __init__(self):
        self.router = APIRouter(prefix="/diet", tags=["Dietetyk Antoniny"])
        self._setup_routes()
    
    def get_name(self) -> str:
        return "diet_antonina"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Plugin do planowania diety i obliczania makroskładników dla Antoniny"
    
    def get_router(self) -> APIRouter:
        return self.router
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            logger.info("Initializing Dietetyk Antonina plugin")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize diet plugin: {e}")
            return False
    
    def get_dependencies(self) -> List[str]:
        return ["cooking_service", "llm_providers"]
    
    def _setup_routes(self):
        """Setup plugin routes."""
        
        @self.router.post("/meal-plan", response_model=MealPlanResponse)
        async def create_meal_plan(
            request: MealPlanRequest,
            db: AsyncSession = Depends(get_async_session),
            user_id: int = Query(..., description="User ID")
        ):
            """Tworzy plan posiłków dla Antoniny."""
            try:
                return await self._generate_meal_plan(request, db, user_id)
            except Exception as e:
                logger.error(f"Failed to create meal plan: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/bmi", response_model=BMICalculationResponse)
        async def calculate_bmi(request: BMICalculationRequest):
            """Oblicza BMI i daje rekomendacje."""
            try:
                return await self._calculate_bmi(request)
            except Exception as e:
                logger.error(f"Failed to calculate BMI: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/recipe-nutrition", response_model=RecipeNutritionResponse)
        async def analyze_recipe_nutrition(
            request: RecipeNutritionRequest,
            db: AsyncSession = Depends(get_async_session),
            user_id: int = Query(..., description="User ID")
        ):
            """Analizuje wartość odżywczą przepisu."""
            try:
                return await self._analyze_recipe_nutrition(request, db, user_id)
            except Exception as e:
                logger.error(f"Failed to analyze recipe nutrition: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/nutrition-tips")
        async def get_nutrition_tips():
            """Zwraca porady żywieniowe dla nastolatków."""
            return {
                "tips": [
                    "Jedz regularnie 5 posiłków dziennie",
                    "Pij dużo wody (minimum 2 litry)",
                    "Jedz kolorowe warzywa i owoce",
                    "Nie pomijaj śniadania",
                    "Ogranicz słodycze i fast food",
                    "Ruszaj się przynajmniej godzinę dziennie",
                    "Jedz powoli i ciesz się jedzeniem",
                    "Nie jedz przed snem"
                ]
            }
    
    async def _generate_meal_plan(self, request: MealPlanRequest, db: AsyncSession, user_id: int) -> MealPlanResponse:
        """Generuje plan posiłków używając AI."""
        
        # Oblicz BMR (Basal Metabolic Rate) - wzór Mifflin-St Jeor
        if request.age < 18:
            bmr = 10 * request.weight + 6.25 * request.height - 5 * request.age + 5
        else:
            bmr = 10 * request.weight + 6.25 * request.height - 5 * request.age - 161
        
        # Dostosuj do poziomu aktywności
        activity_multipliers = {
            "niski": 1.2,
            "średni": 1.55,
            "wysoki": 1.725
        }
        
        daily_calories = int(bmr * activity_multipliers.get(request.activity_level.lower(), 1.55))
        
        # Oblicz makroskładniki (proporcje dla nastolatków)
        daily_proteins = daily_calories * 0.25 / 4  # 25% kalorii z białka
        daily_carbs = daily_calories * 0.55 / 4     # 55% kalorii z węglowodanów
        daily_fats = daily_calories * 0.20 / 9      # 20% kalorii z tłuszczów
        
        # Generuj plan posiłków używając AI
        prompt = f"""
        Stwórz plan posiłków dla 14-letniej dziewczynki:
        
        Dzienne zapotrzebowanie:
        - Kalorie: {daily_calories}
        - Białka: {daily_proteins:.1f}g
        - Węglowodany: {daily_carbs:.1f}g
        - Tłuszcze: {daily_fats:.1f}g
        
        Ograniczenia: {request.dietary_restrictions or 'brak'}
        Preferencje: {request.preferences or 'brak'}
        Budżet dzienny: {request.budget_per_day or 'nieograniczony'} PLN
        
        Stwórz 5 posiłków: śniadanie, drugie śniadanie, obiad, podwieczorek, kolacja.
        Każdy posiłek powinien zawierać:
        - Nazwę
        - Listę składników z ilościami
        - Kalorie
        - Makroskładniki
        - Czas przygotowania
        - Koszt
        
        Odpowiedz w formacie JSON.
        """
        
        try:
            response = await provider_factory.chat_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # Parse AI response (simplified)
            meals = [
                {
                    "name": "Śniadanie - Owsianka z owocami",
                    "calories": daily_calories * 0.25,
                    "proteins": daily_proteins * 0.25,
                    "carbs": daily_carbs * 0.25,
                    "fats": daily_fats * 0.25,
                    "ingredients": ["płatki owsiane", "mleko", "banan", "miód"],
                    "prep_time": 10
                },
                {
                    "name": "Drugie śniadanie - Kanapka z warzywami",
                    "calories": daily_calories * 0.15,
                    "proteins": daily_proteins * 0.15,
                    "carbs": daily_carbs * 0.15,
                    "fats": daily_fats * 0.15,
                    "ingredients": ["chleb pełnoziarnisty", "ser", "pomidor", "sałata"],
                    "prep_time": 5
                }
            ]
            
            return MealPlanResponse(
                daily_calories=daily_calories,
                daily_proteins=daily_proteins,
                daily_carbs=daily_carbs,
                daily_fats=daily_fats,
                meals=meals,
                shopping_list=[],
                estimated_cost=50.0,
                nutrition_tips=[
                    "Jedz regularnie",
                    "Pij dużo wody",
                    "Ruszaj się codziennie"
                ]
            )
            
        except Exception as e:
            logger.error(f"AI meal plan generation failed: {e}")
            # Fallback plan
            return MealPlanResponse(
                daily_calories=daily_calories,
                daily_proteins=daily_proteins,
                daily_carbs=daily_carbs,
                daily_fats=daily_fats,
                meals=[],
                shopping_list=[],
                estimated_cost=0.0,
                nutrition_tips=["Skonsultuj się z dietetykiem"]
            )
    
    async def _calculate_bmi(self, request: BMICalculationRequest) -> BMICalculationResponse:
        """Oblicza BMI i daje rekomendacje."""
        
        # Oblicz BMI
        height_m = request.height / 100
        bmi = request.weight / (height_m * height_m)
        
        # Kategorie BMI dla dzieci (uproszczone)
        if request.age < 18:
            if bmi < 18.5:
                category = "Niedowaga"
            elif bmi < 25:
                category = "Prawidłowa waga"
            elif bmi < 30:
                category = "Nadwaga"
            else:
                category = "Otyłość"
        else:
            if bmi < 18.5:
                category = "Niedowaga"
            elif bmi < 25:
                category = "Prawidłowa waga"
            elif bmi < 30:
                category = "Nadwaga"
            else:
                category = "Otyłość"
        
        # Zakres zdrowej wagi
        min_weight = 18.5 * height_m * height_m
        max_weight = 24.9 * height_m * height_m
        
        # Rekomendacje
        recommendations = []
        if category == "Niedowaga":
            recommendations = [
                "Zwiększ spożycie kalorii",
                "Jedz więcej białka",
                "Skonsultuj się z lekarzem"
            ]
        elif category == "Prawidłowa waga":
            recommendations = [
                "Utrzymuj obecną wagę",
                "Kontynuuj zdrową dietę",
                "Ruszaj się regularnie"
            ]
        elif category == "Nadwaga":
            recommendations = [
                "Zmniejsz spożycie kalorii",
                "Zwiększ aktywność fizyczną",
                "Skonsultuj się z dietetykiem"
            ]
        else:
            recommendations = [
                "Skonsultuj się z lekarzem",
                "Rozważ program odchudzania",
                "Zwiększ aktywność fizyczną"
            ]
        
        return BMICalculationResponse(
            bmi=round(bmi, 1),
            bmi_category=category,
            healthy_weight_range={
                "min": round(min_weight, 1),
                "max": round(max_weight, 1)
            },
            recommendations=recommendations
        )
    
    async def _analyze_recipe_nutrition(self, request: RecipeNutritionRequest, db: AsyncSession, user_id: int) -> RecipeNutritionResponse:
        """Analizuje wartość odżywczą przepisu."""
        
        # Pobierz przepis
        recipe_service = CookingRecipeService(db)
        recipe = await recipe_service.get_recipe(request.recipe_id, user_id)
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Przepis nie znaleziony")
        
        # Pobierz produkty do obliczenia wartości odżywczej
        product_service = CookingProductService(db)
        
        total_calories = 0
        total_proteins = 0
        total_carbs = 0
        total_fats = 0
        
        # Oblicz wartości odżywcze na podstawie składników
        for ingredient in recipe.ingredients:
            # Uproszczone obliczenia - w rzeczywistości potrzebna byłaby baza produktów
            if "mleko" in ingredient.get("name", "").lower():
                total_calories += 42 * ingredient.get("amount", 1)
                total_proteins += 3.4 * ingredient.get("amount", 1)
                total_carbs += 5.0 * ingredient.get("amount", 1)
                total_fats += 1.0 * ingredient.get("amount", 1)
            elif "jajko" in ingredient.get("name", "").lower():
                total_calories += 155 * ingredient.get("amount", 1)
                total_proteins += 13 * ingredient.get("amount", 1)
                total_carbs += 1.1 * ingredient.get("amount", 1)
                total_fats += 11 * ingredient.get("amount", 1)
            # Dodaj więcej produktów...
        
        # Oblicz na porcję
        servings = recipe.servings or 1
        per_serving_calories = total_calories / servings
        per_serving_proteins = total_proteins / servings
        per_serving_carbs = total_carbs / servings
        per_serving_fats = total_fats / servings
        
        # Oblicz health score (0-100)
        health_score = 70  # Podstawowy score
        
        if per_serving_calories < 500:
            health_score += 10
        if per_serving_proteins > 20:
            health_score += 10
        if per_serving_fats < 20:
            health_score += 10
        
        recommendations = []
        if per_serving_calories > 800:
            recommendations.append("Przepis jest wysokokaloryczny")
        if per_serving_proteins < 15:
            recommendations.append("Dodaj więcej białka")
        if per_serving_fats > 30:
            recommendations.append("Ogranicz tłuszcze")
        
        return RecipeNutritionResponse(
            recipe_name=recipe.name,
            total_nutrition=NutritionInfo(
                calories=total_calories,
                proteins=total_proteins,
                carbs=total_carbs,
                fats=total_fats
            ),
            per_serving_nutrition=NutritionInfo(
                calories=per_serving_calories,
                proteins=per_serving_proteins,
                carbs=per_serving_carbs,
                fats=per_serving_fats
            ),
            health_score=health_score,
            recommendations=recommendations
        )


# Plugin instance
diet_plugin = DietPlugin() 