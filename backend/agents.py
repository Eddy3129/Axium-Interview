"""
Two-agent chain: extraction → generation.
Implemented in Phase 3.
"""
from models import RecipeResponse


async def extract_ingredients(raw_input: str) -> list[str]:
    """Strip raw user text down to a clean list of food ingredients."""
    raise NotImplementedError  # TODO Phase 3


async def generate_recipes(ingredients: list[str]) -> RecipeResponse:
    """Generate 2-3 recipes from the validated ingredient list."""
    raise NotImplementedError  # TODO Phase 3
