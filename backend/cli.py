"""
Interactive CLI for the Smart Recipe Analyzer backend.
Requires the backend to be running: uv run main.py

Usage:
    uv run cli.py
"""
import json
import sys

import httpx

BASE_URL = "http://127.0.0.1:8000"


def _print_recipe(index: int, recipe: dict) -> None:
    print(f"\n{'─' * 50}")
    print(f"  Recipe {index}: {recipe['name']}")
    print(f"{'─' * 50}")
    print(f"  Difficulty : {recipe['difficulty']}")
    print(f"  Cook Time  : {recipe['cookingTime']}")

    nutrition = recipe.get("nutrition", {})
    print(f"  Nutrition  : {nutrition.get('calories')} kcal | "
          f"Protein {nutrition.get('protein')} | "
          f"Carbs {nutrition.get('carbs')}")

    print("\n  Ingredients:")
    for item in recipe.get("ingredients", []):
        print(f"    • {item}")

    print("\n  Instructions:")
    for i, step in enumerate(recipe.get("instructions", []), 1):
        print(f"    {i}. {step}")


def _health_check() -> bool:
    try:
        r = httpx.get(f"{BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except httpx.ConnectError:
        return False


def main() -> None:
    print("Smart Recipe Analyzer — CLI")
    print(f"Connecting to {BASE_URL} ...", end=" ")

    if not _health_check():
        print("FAILED")
        print(f"\nError: backend is not running. Start it with:\n  uv run main.py\n")
        sys.exit(1)

    print("OK\n")

    while True:
        try:
            raw = input("Enter ingredients (comma-separated), or 'q' to quit:\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if raw.lower() in ("q", "quit", "exit"):
            print("Bye!")
            break

        if not raw:
            print("  ⚠  Please enter at least one ingredient.\n")
            continue

        print("\nAnalyzing... (this may take a few seconds)\n")

        try:
            response = httpx.post(
                f"{BASE_URL}/recipes",
                json={"ingredients": raw},
                timeout=60,
            )
        except httpx.ConnectError:
            print("  Error: lost connection to backend.\n")
            continue

        if response.status_code == 200:
            data = response.json()
            recipes = data.get("recipes", [])
            print(f"Generated {len(recipes)} recipe(s) for: {raw}")
            for i, recipe in enumerate(recipes, 1):
                _print_recipe(i, recipe)
            print()

        elif response.status_code == 400:
            detail = response.json()
            print(f"  Bad request: {json.dumps(detail, indent=2)}\n")

        elif response.status_code == 422:
            detail = response.json()
            print(f"  LLM returned an unexpected response: {detail.get('message')}\n")

        elif response.status_code == 502:
            detail = response.json()
            print(f"  OpenRouter unavailable: {detail.get('message')}\n")

        else:
            print(f"  Unexpected error {response.status_code}: {response.text}\n")


if __name__ == "__main__":
    main()
