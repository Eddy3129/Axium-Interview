"""
Two-agent chain:
  Agent 1 — extract_ingredients: raw user text → ["ingredient", ...]
  Agent 2 — generate_recipes:   ["ingredient", ...] → RecipeResponse

Both call OpenRouter via the OpenAI-compatible client and use structured
JSON output (json_object mode) to avoid parsing fragile markdown.
"""
import json
import os

from openai import OpenAI, APIConnectionError, APIStatusError
from pydantic import ValidationError as PydanticValidationError

from errors import MalformedLLMResponseError, ExternalServiceUnavailableError, InvalidIngredientsError
from models import RecipeResponse
from prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_VALIDATION_PROMPT, GENERATION_SYSTEM_PROMPT

MODEL = "openai/gpt-4o-mini"


def _get_client() -> OpenAI:
    """Build an OpenAI-compatible client pointed at OpenRouter."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


def _normalize_ingredient_list(values: list) -> list[str]:
    """Normalize ingredient strings and remove obvious invalid entries."""
    normalized: list[str] = []
    seen: set[str] = set()

    for value in values:
        item = str(value).strip().lower()
        if not item:
            continue
        # Keep ingredient-like tokens only (letters, spaces, apostrophes, hyphens).
        if not all(ch.isalpha() or ch in {" ", "-", "'"} for ch in item):
            continue
        item = " ".join(item.split())
        if item and item not in seen:
            normalized.append(item)
            seen.add(item)

    return normalized


def _validate_edible_ingredients(client: OpenAI, candidates: list[str]) -> list[str]:
    """Use a strict validator prompt to keep only edible ingredients."""
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_VALIDATION_PROMPT},
                {"role": "user", "content": json.dumps({"ingredients": candidates})},
            ],
            temperature=0,
            max_tokens=100,
        )
    except APIConnectionError as exc:
        raise ExternalServiceUnavailableError(message=f"Cannot reach OpenRouter: {exc}") from exc
    except APIStatusError as exc:
        raise ExternalServiceUnavailableError(message=f"OpenRouter error {exc.status_code}: {exc.message}") from exc

    raw = completion.choices[0].message.content or ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MalformedLLMResponseError(f"Ingredient validator returned invalid JSON: {raw!r}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("ingredients"), list):
        raise MalformedLLMResponseError("Ingredient validator response missing 'ingredients' array.")

    return _normalize_ingredient_list(payload["ingredients"])


async def extract_ingredients(raw_input: str) -> list[str]:
    """
    Agent 1: Parse raw user text and return a clean list of food ingredient strings.
    Raises:
        InvalidIngredientsError  — no valid food ingredients found
        MalformedLLMResponseError — LLM returned invalid JSON
        ExternalServiceUnavailableError — OpenRouter unreachable
    """
    client = _get_client()
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": raw_input},
            ],
            temperature=0,
            max_tokens=100,
        )
    except APIConnectionError as exc:
        raise ExternalServiceUnavailableError(message=f"Cannot reach OpenRouter: {exc}") from exc
    except APIStatusError as exc:
        raise ExternalServiceUnavailableError(message=f"OpenRouter error {exc.status_code}: {exc.message}") from exc

    raw = completion.choices[0].message.content or ""

    # Parse the JSON response. The extraction prompt tries to return a bare array,
    # but json_object mode may force it to wrap in an object, so we handle both cases.
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            # Bare array: ["ingredient", ...]
            ingredients = parsed
        elif isinstance(parsed, dict):
            # Wrapped object: {"ingredients": [...]} or similar
            ingredients = next(
                (v for v in parsed.values() if isinstance(v, list)), []
            )
        else:
            raise ValueError("Expected JSON array or object with array value")
    except (json.JSONDecodeError, ValueError) as exc:
        raise MalformedLLMResponseError(f"Extraction agent returned invalid JSON: {raw!r}") from exc

    ingredients = _normalize_ingredient_list(ingredients)

    if not ingredients:
        raise InvalidIngredientsError(["No valid food ingredients could be extracted from the input."])

    ingredients = _validate_edible_ingredients(client, ingredients)

    if not ingredients:
        raise InvalidIngredientsError([
            "No edible food ingredients found after validation.",
            "Provide edible ingredients like 'chicken, lemon, rice'.",
        ])

    return ingredients


async def generate_recipes(ingredients: list[str]) -> RecipeResponse:
    """
    Agent 2: Generate 2-3 recipes from a clean ingredient list.
    Raises:
        MalformedLLMResponseError        — LLM returned invalid JSON or failed schema validation
        ExternalServiceUnavailableError  — OpenRouter unreachable
    """
    client = _get_client()
    user_message = (
        f"Generate recipes using these ingredients: {json.dumps(ingredients)}\n"
        "Return a JSON object with a \"recipes\" key containing 2 or 3 recipes."
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
    except APIConnectionError as exc:
        raise ExternalServiceUnavailableError(message=f"Cannot reach OpenRouter: {exc}") from exc
    except APIStatusError as exc:
        raise ExternalServiceUnavailableError(message=f"OpenRouter error {exc.status_code}: {exc.message}") from exc

    raw = completion.choices[0].message.content or ""

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MalformedLLMResponseError(f"Generation agent returned invalid JSON: {raw!r}") from exc

    try:
        return RecipeResponse.model_validate(payload)
    except PydanticValidationError as exc:
        raise MalformedLLMResponseError(
            f"Generation agent response failed schema validation: {exc.error_count()} error(s) — "
            + "; ".join(e["msg"] for e in exc.errors())
        ) from exc
