"use client";

import { useState } from "react";

interface SaveRecipeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (rating: number) => Promise<void>;
  isSaving: boolean;
  errorMessage: string | null;
}

export default function SaveRecipeModal({
  isOpen,
  onClose,
  onSave,
  isSaving,
  errorMessage,
}: SaveRecipeModalProps) {
  const [rating, setRating] = useState(0);
  const [hovered, setHovered] = useState(0);

  if (!isOpen) return null;

  const displayRating = hovered || rating;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Save recipe"
    >
      <div className="save-modal">
        <h3>Save Recipe</h3>
        <p>Rate this recipe before saving it to your collection.</p>

        <div className="star-row" aria-label="Star rating from 1 to 5">
          {[1, 2, 3, 4, 5].map((star) => {
            const filled = star <= displayRating;
            return (
              <button
                key={star}
                type="button"
                className={`star-btn ${filled ? "filled" : ""}`}
                onMouseEnter={() => setHovered(star)}
                onMouseLeave={() => setHovered(0)}
                onClick={() => setRating(star)}
                aria-label={`Rate ${star} star${star > 1 ? "s" : ""}`}
              >
                ★
              </button>
            );
          })}
        </div>

        {errorMessage && <p className="error-text">{errorMessage}</p>}

        <div className="modal-actions">
          <button
            className="modal-btn secondary"
            onClick={onClose}
            disabled={isSaving}
          >
            Cancel
          </button>
          <button
            className="modal-btn primary"
            onClick={() => void onSave(rating)}
            disabled={isSaving || rating < 1}
          >
            {isSaving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}
