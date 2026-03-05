# Smart Recipe Analyzer — MVP Plan

> Source of truth: `INSTRUCTIONS.md`

## Tech Stack

| Layer      | Technology             |
| ---------- | ---------------------- |
| Frontend   | Next.js (App Router)   |
| Backend    | FastAPI + Uvicorn      |
| Validation | Pydantic v2            |
| LLM API    | OpenRouter (any model) |
| Testing    | Pytest                 |

---

## Project Structure

```
FoodApp/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Pydantic schemas
│   ├── agents.py            # Extraction + Generation agents
│   ├── prompts.py           # System/user prompt templates
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py
└── frontend/
    ├── app/
    │   ├── page.tsx         # Main UI (input + results)
    │   └── layout.tsx
    ├── components/
    │   ├── IngredientForm.tsx
    │   ├── RecipeCard.tsx
    │   └── LoadingSpinner.tsx
    └── package.json
```

---

## Phase 1 — Project Scaffolding

**Goal:** Runnable skeleton with no business logic yet.

- [ ] Init `backend/` — `pip install fastapi uvicorn pydantic openai pytest httpx`
- [ ] Init `frontend/` — `npx create-next-app@latest` (TypeScript, Tailwind)
- [ ] Create `backend/.env` with `OPENROUTER_API_KEY`
- [ ] Add `backend/main.py` with a single `GET /health` route returning `{"status": "ok"}`
- [ ] Verify both servers start: `uvicorn main:app --reload` and `npm run dev`

**Exit criteria:** Both servers run locally with no errors.

---

## Phase 2 — Pydantic Models

**Goal:** Define the data contract that the entire app is built around.

File: `backend/models.py`

```python
from enum import Enum
from pydantic import BaseModel

class Difficulty(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"

class Nutrition(BaseModel):
    calories: int
    protein: str   # e.g. "12g"
    carbs: str     # e.g. "60g"

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
    ingredients: str   # raw user input, comma-separated
```

**Exit criteria:** Models import cleanly; no validation errors on a sample dict.

---

## Phase 3 — Prompt Engineering & Agents

**Goal:** Two-agent chain: Extraction → Generation.

File: `backend/prompts.py`

- **Extraction system prompt** — instructs the LLM to return only a clean JSON array of valid food ingredient strings from the raw user input (ignores quantities, units, non-food words)
- **Generation system prompt** — instructs the LLM to generate exactly 2–3 recipes from the ingredient list and return a JSON object matching `RecipeResponse`

File: `backend/agents.py`

```
extract_ingredients(raw_input: str) -> list[str]
  → calls OpenRouter with extraction prompt
  → returns parsed list[str]

generate_recipes(ingredients: list[str]) -> RecipeResponse
  → calls OpenRouter with generation prompt
  → parses and validates response against RecipeResponse model
```

**Exit criteria:** Both functions testable in isolation via `pytest`; `generate_recipes` returns a valid `RecipeResponse`.

---

## Phase 4 — Backend API Endpoint

**Goal:** Single `POST /recipes` endpoint wiring together both agents.

File: `backend/main.py`

```
POST /recipes
  Body: { "ingredients": "chicken, garlic, lemon, pasta" }

  1. Validate body is not empty (400 if blank)
  2. Call extract_ingredients()
  3. Call generate_recipes()
  4. Return RecipeResponse JSON

  Error responses:
    400 — empty ingredients
    422 — LLM returned malformed JSON
    502 — OpenRouter unreachable
```

- [ ] Add CORS middleware to allow `localhost:3000`

**Exit criteria:** `curl -X POST /recipes` with sample ingredients returns valid JSON matching the schema in `INSTRUCTIONS.md`.

---

## Phase 5 — Frontend UI

**Goal:** Functional, responsive UI with all states covered.

Components:

| Component        | Responsibility                                                                                     |
| ---------------- | -------------------------------------------------------------------------------------------------- |
| `IngredientForm` | Textarea + submit button; validates input is not empty before submitting                           |
| `LoadingSpinner` | Shown while awaiting API response                                                                  |
| `RecipeCard`     | Renders one recipe: name, difficulty, cookingTime, ingredients list, instructions, nutrition table |
| `page.tsx`       | Composes the above; manages `idle / loading / success / error` state                               |

Requirements from `INSTRUCTIONS.md`:

- [ ] Textarea accepts comma-separated ingredients
- [ ] Loading indicator shown during API call
- [ ] Error message shown if API fails
- [ ] Responsive layout (desktop + mobile via Tailwind)

**Exit criteria:** UI renders all three recipe cards from a mocked API response; loading and error states display correctly.

---

## Phase 6 — Frontend ↔ Backend Integration

**Goal:** End-to-end flow working locally.

- [ ] Create `frontend/lib/api.ts` — typed `fetchRecipes(ingredients: string)` function calling `POST http://localhost:8000/recipes`
- [ ] Wire `IngredientForm` submit → `fetchRecipes` → render `RecipeCard` list
- [ ] Test full flow end-to-end with real OpenRouter call

**Exit criteria:** User enters ingredients, clicks submit, sees 2–3 recipe cards with nutritional info. Matches the full flow described in `INSTRUCTIONS.md`.

---

## Phase 7 — Tests & Cleanup

**Goal:** Confidence the MVP works reliably before demo.

- [ ] `tests/test_api.py` — pytest tests for:
  - `POST /recipes` with valid input returns 200 + correct schema
  - `POST /recipes` with empty input returns 400
- [ ] Smoke-test extraction agent with non-food input (e.g. "table, run, 500ml")
- [ ] Remove all debug `print` statements
- [ ] Add `README.md` with setup instructions (`how to run backend`, `how to run frontend`, `env vars needed`)

**Exit criteria:** All pytest tests pass; app runs cleanly from a fresh clone following the README.

---

## Out of Scope for MVP

The following bonus features from `INSTRUCTIONS.md` are explicitly deferred:

- Dietary restriction filters
- Recipe rating
- Ingredient substitutions
- Recipe history / persistence
- Image generation (DALL-E)
