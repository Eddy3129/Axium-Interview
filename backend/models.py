"""
Pydantic models for the Smart Recipe Analyzer API.
Includes data validation, error classifications, and API contracts.
"""
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Difficulty(str, Enum):
    """Cooking difficulty level."""
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class Nutrition(BaseModel):
    """Nutritional information for a recipe."""
    calories: int = Field(..., gt=0, description="Calories per serving (must be > 0)")
    protein: str = Field(..., min_length=1, max_length=10, description="Protein content (e.g., '12g')")
    carbs: str = Field(..., min_length=1, max_length=10, description="Carbohydrate content (e.g., '60g')")

    @field_validator("protein", "carbs", mode="before")
    @classmethod
    def validate_nutrition_format(cls, v: str) -> str:
        """Ensure nutrition values end with a unit (g, mg, etc.)."""
        if not isinstance(v, str):
            raise ValueError("Must be a string")
        if not any(v.endswith(unit) for unit in ["g", "mg", "oz", "%"]):
            raise ValueError("Must end with a unit (g, mg, oz, %)")
        return v


class Recipe(BaseModel):
    """A single recipe suggestion."""
    name: str = Field(..., min_length=1, max_length=100, description="Recipe name")
    ingredients: list[str] = Field(default_factory=list, description="List of ingredients")
    instructions: list[str] = Field(default_factory=list, description="Cooking steps")
    cookingTime: str = Field(..., min_length=1, max_length=50, description="Estimated cooking duration (e.g., '20 minutes')")
    difficulty: Difficulty = Field(..., description="Difficulty level: Easy, Medium, or Hard")
    nutrition: Nutrition = Field(..., description="Nutritional information")

    @field_validator("ingredients", "instructions", mode="before")
    @classmethod
    def validate_lists_not_empty(cls, v: list) -> list:
        """Ensure ingredient and instruction lists are not empty."""
        if not v or len(v) == 0:
            raise ValueError("Must contain at least one item")
        return v


class RecipeResponse(BaseModel):
    """API response containing generated recipes."""
    recipes: list[Recipe] = Field(..., min_items=2, max_items=3, description="Generated recipes (1-3 recipes)")


class IngredientsRequest(BaseModel):
    """API request for recipe generation."""
    ingredients: str = Field(..., min_length=1, max_length=500, description="Comma-separated ingredients provided by user")

    @field_validator("ingredients", mode="before")
    @classmethod
    def validate_not_empty_or_whitespace(cls, v: str) -> str:
        """Reject empty or whitespace-only input."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Ingredients cannot be empty or whitespace only")
        return v.strip()


class SaveRecipeRequest(BaseModel):
    """Request to persist a generated recipe with a user rating."""
    recipe: Recipe = Field(..., description="Recipe object to save")
    rating: int = Field(..., ge=1, le=5, description="User rating from 1 to 5")


class SavedRecipe(BaseModel):
    """Persisted recipe record with DB metadata."""
    id: int = Field(..., ge=1, description="Database primary key")
    recipe: Recipe = Field(..., description="Saved recipe payload")
    rating: int = Field(..., ge=1, le=5, description="User rating from 1 to 5")
    createdAt: str = Field(..., description="UTC ISO timestamp when recipe was saved")


class SavedRecipeListResponse(BaseModel):
    """Response model for listing saved recipes."""
    items: list[SavedRecipe] = Field(default_factory=list, description="Saved recipe list")


# ============================================================================
# Error Models — API error responses
# ============================================================================


class ErrorDetail(BaseModel):
    """Generic error detail."""
    code: str = Field(..., description="Error code (e.g., 'invalid_input')")
    message: str = Field(..., description="Human-readable error message")


class ValidationError(BaseModel):
    """400 Bad Request — validation failure."""
    error: str = Field(default="validation_error", description="Error type")
    details: list[ErrorDetail] = Field(default_factory=list, description="List of validation failures")


class MalformedLLMResponse(BaseModel):
    """422 Unprocessable Entity — LLM returned invalid JSON."""
    error: str = Field(default="malformed_llm_response", description="Error type")
    message: str = Field(..., description="Details about malformed response")


class ExternalServiceError(BaseModel):
    """502 Bad Gateway — OpenRouter or external service unavailable."""
    error: str = Field(default="external_service_error", description="Error type")
    message: str = Field(..., description="Details about the service failure")
