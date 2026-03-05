import pytest
from pydantic import ValidationError as PydanticValidationError

from models import (
    Difficulty,
    IngredientsRequest,
    Nutrition,
    Recipe,
    RecipeResponse,
    SaveRecipeRequest,
)


def make_valid_recipe() -> Recipe:
    return Recipe(
        name="Lemon Garlic Chicken",
        ingredients=["chicken", "lemon", "garlic"],
        instructions=["Season chicken.", "Pan-sear.", "Add lemon and finish."],
        cookingTime="25 minutes",
        difficulty=Difficulty.easy,
        nutrition=Nutrition(calories=430, protein="38g", carbs="8g"),
    )


def test_ingredients_request_strips_whitespace():
    payload = IngredientsRequest(ingredients="  chicken, lemon  ")
    assert payload.ingredients == "chicken, lemon"


def test_ingredients_request_rejects_blank():
    with pytest.raises(PydanticValidationError):
        IngredientsRequest(ingredients="   ")


def test_nutrition_rejects_non_positive_calories():
    with pytest.raises(PydanticValidationError):
        Nutrition(calories=0, protein="10g", carbs="30g")


def test_nutrition_rejects_missing_unit():
    with pytest.raises(PydanticValidationError):
        Nutrition(calories=220, protein="10", carbs="30g")


def test_recipe_rejects_empty_instructions():
    with pytest.raises(PydanticValidationError):
        Recipe(
            name="Bad Recipe",
            ingredients=["egg"],
            instructions=[],
            cookingTime="10 minutes",
            difficulty=Difficulty.easy,
            nutrition=Nutrition(calories=120, protein="6g", carbs="1g"),
        )


def test_recipe_response_rejects_out_of_range_count():
    valid = make_valid_recipe()
    with pytest.raises(PydanticValidationError):
        RecipeResponse(recipes=[valid])

    with pytest.raises(PydanticValidationError):
        RecipeResponse(recipes=[valid, valid, valid, valid])


def test_save_recipe_request_accepts_rating_1_to_5_only():
    valid_recipe = make_valid_recipe()

    ok = SaveRecipeRequest(recipe=valid_recipe, rating=5)
    assert ok.rating == 5

    with pytest.raises(PydanticValidationError):
        SaveRecipeRequest(recipe=valid_recipe, rating=0)

    with pytest.raises(PydanticValidationError):
        SaveRecipeRequest(recipe=valid_recipe, rating=6)
