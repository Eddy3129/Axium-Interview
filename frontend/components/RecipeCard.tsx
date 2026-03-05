"use client";

import { useState } from "react";
import type { Recipe } from "@/types/recipe";

interface RecipeCardProps {
  recipe: Recipe;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const [open, setOpen] = useState(false);

  return (
    <article className="recipe-card">
      <div className="recipe-header">
        <div>
          <h3>{recipe.name}</h3>
          <p className="recipe-meta">
            {recipe.difficulty} · {recipe.cookingTime}
          </p>
        </div>
        <button className="expand-btn" onClick={() => setOpen((v) => !v)}>
          {open ? "Collapse" : "Expand"}
        </button>
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
  );
}
