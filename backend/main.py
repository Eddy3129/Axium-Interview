from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()  # loads backend/.env into os.environ

from db import init_db, list_saved_recipes as db_list_saved_recipes, save_recipe as db_save_recipe


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Add it to backend/.env")
    init_db()
    yield


app = FastAPI(
    title="Smart Recipe Analyzer",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers — map custom errors to HTTP status codes
# ---------------------------------------------------------------------------
from errors import (
    InvalidIngredientsError,
    MalformedLLMResponseError,
    ExternalServiceUnavailableError,
)


@app.exception_handler(InvalidIngredientsError)
async def invalid_ingredients_handler(request: Request, exc: InvalidIngredientsError):
    return JSONResponse(status_code=400, content=exc.to_pydantic().model_dump())


@app.exception_handler(MalformedLLMResponseError)
async def malformed_llm_handler(request: Request, exc: MalformedLLMResponseError):
    return JSONResponse(status_code=422, content=exc.to_pydantic().model_dump())


@app.exception_handler(ExternalServiceUnavailableError)
async def external_service_handler(request: Request, exc: ExternalServiceUnavailableError):
    return JSONResponse(status_code=502, content=exc.to_pydantic().model_dump())


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
from agents import extract_ingredients, generate_recipes
from models import (
    ErrorDetail,
    IngredientsRequest,
    RecipeResponse,
    SaveRecipeRequest,
    SavedRecipe,
    SavedRecipeListResponse,
    ValidationError as ApiValidationError,
)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    details = [
        ErrorDetail(code="invalid_input", message=err.get("msg", "Invalid input"))
        for err in exc.errors()
    ]
    payload = ApiValidationError(details=details)
    return JSONResponse(status_code=400, content=payload.model_dump())


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/recipes", response_model=RecipeResponse)
async def recipes(body: IngredientsRequest) -> RecipeResponse:
    """
    POST /recipes
    Body: { "ingredients": "chicken, garlic, lemon" }

    1. Validate input (Pydantic — 400 if blank)
    2. Extract clean ingredients via LLM agent 1
    3. Generate recipes via LLM agent 2
    4. Return validated RecipeResponse
    """
    ingredients = await extract_ingredients(body.ingredients)
    return await generate_recipes(ingredients)


@app.post("/saved-recipes", response_model=SavedRecipe)
async def save_saved_recipe(body: SaveRecipeRequest) -> SavedRecipe:
    """Persist one recipe with a user rating in SQLite."""
    return db_save_recipe(body)


@app.get("/saved-recipes", response_model=SavedRecipeListResponse)
async def get_saved_recipes() -> SavedRecipeListResponse:
    """List saved recipes for frontend rendering."""
    return SavedRecipeListResponse(items=db_list_saved_recipes())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
