import type { ApiError, RecipeResponse } from "@/types/recipe";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

function toErrorMessage(status: number, payload: ApiError | null): string {
  if (payload?.message) return payload.message;
  if (payload?.details?.length)
    return payload.details.map((d) => d.message).join("; ");
  if (status === 400) return "Please provide valid ingredients.";
  if (status === 422)
    return "The AI response could not be processed. Please retry.";
  if (status === 502)
    return "Recipe service is temporarily unavailable. Please retry shortly.";
  return "Unexpected server error. Please try again.";
}

export async function fetchRecipes(
  ingredients: string,
): Promise<RecipeResponse> {
  const response = await fetch(`${API_BASE_URL}/recipes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ingredients }),
  });

  if (!response.ok) {
    let payload: ApiError | null = null;
    try {
      payload = (await response.json()) as ApiError;
    } catch {
      payload = null;
    }

    throw new Error(toErrorMessage(response.status, payload));
  }

  return (await response.json()) as RecipeResponse;
}
