"use client";

import { useState } from "react";
import { saveRecipe } from "@/lib/api";
import SaveRecipeModal from "@/components/SaveRecipeModal";
import type { Recipe } from "@/types/recipe";

interface RecipeCardProps {
  recipe: Recipe;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const [open, setOpen] = useState(false);
  const [isModalOpen, setModalOpen] = useState(false);
  const [isSaving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [savedRating, setSavedRating] = useState<number | null>(null);

  const handleSave = async (rating: number) => {
    setSaveError(null);
    setSaving(true);
    try {
      await saveRecipe(recipe, rating);
      setSavedRating(rating);
      setModalOpen(false);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to save recipe.";
      setSaveError(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <article className="recipe-card">
        <div className="recipe-header">
          <div>
            <h3>{recipe.name}</h3>
            <p className="recipe-meta">
              {recipe.difficulty} · {recipe.cookingTime}
            </p>
          </div>
          <div className="recipe-actions">
            <button className="save-btn" onClick={() => setModalOpen(true)}>
              {savedRating ? `Saved (${savedRating}/5)` : "Save"}
            </button>
            <button className="expand-btn" onClick={() => setOpen((v) => !v)}>
              {open ? "Collapse" : "Expand"}
            </button>
          </div>
        </div>

        <div className="nutrition-strip">
          <span>{recipe.nutrition.calories} kcal</span>
          <span>Protein {recipe.nutrition.protein}</span>
          <span>Carbs {recipe.nutrition.carbs}</span>
        </div>

        {open && (
          <div className="recipe-details">
            <div>
              <h4>Ingredients</h4>
              <ul>
                {recipe.ingredients.map((item, idx) => (
                  <li key={`${item}-${idx}`}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4>Instructions</h4>
              <ol>
                {recipe.instructions.map((step, idx) => (
                  <li key={`${step}-${idx}`}>{step}</li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </article>

      {isModalOpen && (
        <SaveRecipeModal
          isOpen={isModalOpen}
          onClose={() => setModalOpen(false)}
          onSave={handleSave}
          isSaving={isSaving}
          errorMessage={saveError}
        />
      )}
    </>
  );
}
