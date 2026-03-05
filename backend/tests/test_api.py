"""
API integration tests — expanded in Phase 7.
"""
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport
from pydantic import ValidationError as PydanticValidationError

# Add parent directory to path so we can import from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from models import (
    IngredientsRequest,
    Difficulty,
    Nutrition,
    Recipe,
    RecipeResponse,
)


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ============================================================================
# Phase 2: Pydantic Model Validation Tests
# ============================================================================


class TestIngredientsRequest:
    """Test IngredientsRequest validation."""
    
    def test_valid_ingredients(self):
        """Valid comma-separated input."""
        req = IngredientsRequest(ingredients="chicken, garlic, lemon")
        assert req.ingredients == "chicken, garlic, lemon"
    
    def test_empty_ingredients_rejected(self):
        """Empty string is rejected."""
        with pytest.raises(PydanticValidationError):
            IngredientsRequest(ingredients="")
    
    def test_whitespace_only_rejected(self):
        """Whitespace-only input is rejected."""
        with pytest.raises(PydanticValidationError):
            IngredientsRequest(ingredients="   ")


class TestNutrition:
    """Test Nutrition model validation."""
    
    def test_valid_nutrition(self):
        """Valid nutrition data."""
        nut = Nutrition(calories=450, protein="12g", carbs="60g")
        assert nut.calories == 450
        assert nut.protein == "12g"
    
    def test_nutrition_calories_must_be_positive(self):
        """Calories must be > 0."""
        with pytest.raises(PydanticValidationError):
            Nutrition(calories=0, protein="12g", carbs="60g")
    
    def test_nutrition_protein_must_have_unit(self):
        """Protein string must end with unit."""
        with pytest.raises(PydanticValidationError):
            Nutrition(calories=450, protein="12", carbs="60g")
    
    def test_nutrition_carbs_accepts_percent(self):
        """Carbs can use % as unit."""
        nut = Nutrition(calories=450, protein="12g", carbs="50%")
        assert nut.carbs == "50%"


class TestRecipe:
    """Test Recipe model validation."""
    
    def test_valid_recipe(self):
        """Valid recipe with all required fields."""
        recipe = Recipe(
            name="Pasta",
            ingredients=["pasta", "garlic"],
            instructions=["Boil pasta", "Sauté garlic"],
            cookingTime="20 minutes",
            difficulty=Difficulty.easy,
            nutrition=Nutrition(calories=450, protein="12g", carbs="60g"),
        )
        assert recipe.name == "Pasta"
        assert len(recipe.ingredients) == 2
    
    def test_recipe_empty_ingredients_rejected(self):
        """Recipe must have at least one ingredient."""
        with pytest.raises(PydanticValidationError):
            Recipe(
                name="Pasta",
                ingredients=[],
                instructions=["Boil pasta"],
                cookingTime="20 minutes",
                difficulty=Difficulty.easy,
                nutrition=Nutrition(calories=450, protein="12g", carbs="60g"),
            )
    
    def test_recipe_empty_instructions_rejected(self):
        """Recipe must have at least one instruction."""
        with pytest.raises(PydanticValidationError):
            Recipe(
                name="Pasta",
                ingredients=["pasta"],
                instructions=[],
                cookingTime="20 minutes",
                difficulty=Difficulty.easy,
                nutrition=Nutrition(calories=450, protein="12g", carbs="60g"),
            )


class TestRecipeResponse:
    """Test RecipeResponse model validation."""
    
    def test_valid_response_with_three_recipes(self):
        """Valid response with max recipes."""
        recipes = [
            Recipe(
                name=f"Recipe {i}",
                ingredients=["ingredient"],
                instructions=["step"],
                cookingTime="20 min",
                difficulty=Difficulty.easy,
                nutrition=Nutrition(calories=450, protein="12g", carbs="60g"),
            )
            for i in range(3)
        ]
        resp = RecipeResponse(recipes=recipes)
        assert len(resp.recipes) == 3
    
    def test_response_empty_recipes_rejected(self):
        """Response must contain at least one recipe."""
        with pytest.raises(PydanticValidationError):
            RecipeResponse(recipes=[])
    
    def test_response_too_many_recipes_rejected(self):
        """Response cannot have more than 3 recipes."""
        recipes = [
            Recipe(
                name=f"Recipe {i}",
                ingredients=["ingredient"],
                instructions=["step"],
                cookingTime="20 min",
                difficulty=Difficulty.easy,
                nutrition=Nutrition(calories=450, protein="12g", carbs="60g"),
            )
            for i in range(4)
        ]
        with pytest.raises(PydanticValidationError):
            RecipeResponse(recipes=recipes)
