export type Difficulty = "Easy" | "Medium" | "Hard";

export interface Nutrition {
  calories: number;
  protein: string;
  carbs: string;
}

export interface Recipe {
  name: string;
  ingredients: string[];
  instructions: string[];
  cookingTime: string;
  difficulty: Difficulty;
  nutrition: Nutrition;
}

export interface RecipeResponse {
  recipes: Recipe[];
}

export interface SaveRecipeRequest {
  recipe: Recipe;
  rating: number;
}

export interface SavedRecipe {
  id: number;
  recipe: Recipe;
  rating: number;
  createdAt: string;
}

export interface SavedRecipeListResponse {
  items: SavedRecipe[];
}

export interface ApiError {
  error: string;
  message?: string;
  details?: Array<{ code: string; message: string }>;
}
