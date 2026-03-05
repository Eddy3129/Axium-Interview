from enum import Enum

from pydantic import BaseModel


class Difficulty(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class Nutrition(BaseModel):
    calories: int
    protein: str  # e.g. "12g"
    carbs: str    # e.g. "60g"


class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    instructions: list[str]
    cookingTime: str
    difficulty: Difficulty
    nutrition: Nutrition


class RecipeResponse(BaseModel):
    recipes: list[Recipe]


class IngredientsRequest(BaseModel):
    ingredients: str  # raw comma-separated user input
