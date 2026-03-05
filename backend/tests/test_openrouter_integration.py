import os

import pytest
from httpx import ASGITransport, AsyncClient

from agents import extract_ingredients, generate_recipes
from main import app
from models import RecipeResponse


def _has_real_openrouter_key() -> bool:
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key:
        return False
    if key == "your_openrouter_api_key_here":
        return False
    return True


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _has_real_openrouter_key(),
        reason="OPENROUTER_API_KEY missing or placeholder; integration tests require live API.",
    ),
]


@pytest.mark.asyncio
async def test_live_extraction_filters_non_food_entities():
    raw = "Donald trump, chicken, lemon"
    ingredients = await extract_ingredients(raw)

    assert "chicken" in ingredients
    assert "lemon" in ingredients
    assert all("donald" not in item and "trump" not in item for item in ingredients)


@pytest.mark.asyncio
async def test_live_generation_returns_schema_valid_response():
    ingredients = ["chicken", "lemon", "garlic", "rice"]
    result = await generate_recipes(ingredients)

    assert isinstance(result, RecipeResponse)
    assert 2 <= len(result.recipes) <= 3
    for recipe in result.recipes:
        assert recipe.name
        assert recipe.ingredients
        assert recipe.instructions
        assert recipe.nutrition.calories > 0


@pytest.mark.asyncio
async def test_live_recipes_endpoint_end_to_end():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/recipes", json={"ingredients": "chicken, garlic, lemon"}, timeout=120)

    assert response.status_code == 200
    payload = response.json()
    assert "recipes" in payload
    assert 2 <= len(payload["recipes"]) <= 3
