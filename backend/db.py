import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from models import (
    Difficulty,
    Nutrition,
    Recipe,
    SaveRecipeRequest,
    SavedRecipe,
)

DB_PATH = Path(__file__).resolve().parent / "recipes.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ingredients_json TEXT NOT NULL,
                instructions_json TEXT NOT NULL,
                cooking_time TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein TEXT NOT NULL,
                carbs TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_recipe(payload: SaveRecipeRequest) -> SavedRecipe:
    now_utc = datetime.now(timezone.utc).isoformat()
    recipe = payload.recipe

    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO saved_recipes (
                name,
                ingredients_json,
                instructions_json,
                cooking_time,
                difficulty,
                calories,
                protein,
                carbs,
                rating,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recipe.name,
                json.dumps(recipe.ingredients),
                json.dumps(recipe.instructions),
                recipe.cookingTime,
                recipe.difficulty.value,
                recipe.nutrition.calories,
                recipe.nutrition.protein,
                recipe.nutrition.carbs,
                payload.rating,
                now_utc,
            ),
        )
        conn.commit()

    return SavedRecipe(
        id=int(cursor.lastrowid),
        recipe=recipe,
        rating=payload.rating,
        createdAt=now_utc,
    )


def list_saved_recipes() -> list[SavedRecipe]:
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                name,
                ingredients_json,
                instructions_json,
                cooking_time,
                difficulty,
                calories,
                protein,
                carbs,
                rating,
                created_at
            FROM saved_recipes
            ORDER BY id DESC
            """
        ).fetchall()

    items: list[SavedRecipe] = []
    for row in rows:
        recipe = Recipe(
            name=row["name"],
            ingredients=json.loads(row["ingredients_json"]),
            instructions=json.loads(row["instructions_json"]),
            cookingTime=row["cooking_time"],
            difficulty=Difficulty(row["difficulty"]),
            nutrition=Nutrition(
                calories=row["calories"],
                protein=row["protein"],
                carbs=row["carbs"],
            ),
        )
        items.append(
            SavedRecipe(
                id=row["id"],
                recipe=recipe,
                rating=row["rating"],
                createdAt=row["created_at"],
            )
        )

    return items
