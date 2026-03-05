"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchSavedRecipes } from "@/lib/api";
import type { SavedRecipe } from "@/types/recipe";

function starRow(rating: number) {
  return "★★★★★".slice(0, rating) + "☆☆☆☆☆".slice(0, 5 - rating);
}

export default function RecipesPage() {
  const [items, setItems] = useState<SavedRecipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openMap, setOpenMap] = useState<Record<number, boolean>>({});

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const data = await fetchSavedRecipes();
        if (!mounted) return;
        setItems(data.items);
      } catch (err) {
        if (!mounted) return;
        setError(
          err instanceof Error ? err.message : "Failed to load saved recipes.",
        );
      } finally {
        if (mounted) setLoading(false);
      }
    };

    void load();

    return () => {
      mounted = false;
    };
  }, []);

  const orderedItems = useMemo(
    () =>
      [...items].sort(
        (a, b) =>
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
      ),
    [items],
  );

  return (
    <main className="recipes-page">
      <header className="recipes-header">
        <h1>Saved Recipes</h1>
        <p>Your saved recipe history in newest-first order.</p>
      </header>

      {loading && <p className="recipes-note">Loading saved recipes...</p>}
      {error && !loading && <p className="error-text">{error}</p>}

      {!loading && !error && orderedItems.length === 0 && (
        <p className="recipes-note">
          No recipes saved yet. Save from the chat page.
        </p>
      )}

      {!loading && !error && orderedItems.length > 0 && (
        <ul className="saved-recipes-list">
          {orderedItems.map((item) => (
            <li key={item.id} className="saved-recipe-item">
              <div className="saved-recipe-head">
                <h3>{item.recipe.name}</h3>
                <span className="saved-time">
                  {new Date(item.createdAt).toLocaleString()}
                </span>
              </div>
              <div className="saved-recipe-actions">
                <button
                  className="expand-btn"
                  onClick={() =>
                    setOpenMap((prev) => ({
                      ...prev,
                      [item.id]: !prev[item.id],
                    }))
                  }
                >
                  {openMap[item.id] ? "Hide Instructions" : "View Instructions"}
                </button>
              </div>
              <p className="saved-meta">
                {item.recipe.difficulty} · {item.recipe.cookingTime}
              </p>
              <p className="saved-rating">
                Rating: {starRow(item.rating)} ({item.rating}/5)
              </p>
              <div className="nutrition-strip">
                <span>{item.recipe.nutrition.calories} kcal</span>
                <span>Protein {item.recipe.nutrition.protein}</span>
                <span>Carbs {item.recipe.nutrition.carbs}</span>
              </div>

              {openMap[item.id] && (
                <div className="saved-instructions">
                  <h4>Instructions</h4>
                  <ol>
                    {item.recipe.instructions.map((step, idx) => (
                      <li key={`${item.id}-step-${idx}`}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
