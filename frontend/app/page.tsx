"use client";

import { useState } from "react";
import ChatInput from "@/components/ChatInput";
import ChatMessage from "@/components/ChatMessage";
import RecipeCard from "@/components/RecipeCard";
import RecipeSkeleton from "@/components/RecipeSkeleton";
import { fetchRecipes } from "@/lib/api";
import type { Recipe } from "@/types/recipe";

type ChatItem =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; recipes: Recipe[] }
  | { id: string; role: "assistant"; error: string };

function makeId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function Home() {
  const [messages, setMessages] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (text: string) => {
    const userId = makeId();
    setMessages((prev) => [...prev, { id: userId, role: "user", text }]);
    setLoading(true);

    try {
      const data = await fetchRecipes(text);
      setMessages((prev) => [
        ...prev,
        { id: makeId(), role: "assistant", recipes: data.recipes },
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        { id: makeId(), role: "assistant", error: message },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="chat-shell">
      <header className="chat-header">
        <h1>Smart Recipe Analyzer</h1>
        <p>
          Send your available ingredients and get AI-generated recipes with
          nutrition.
        </p>
      </header>

      <section className="chat-feed" aria-live="polite">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Start by sending ingredients like:</p>
            <code>chicken, garlic, lemon, pasta</code>
          </div>
        )}

        {messages.map((item) => {
          if ("text" in item) {
            return (
              <ChatMessage key={item.id} role="user">
                <p>{item.text}</p>
              </ChatMessage>
            );
          }

          if ("error" in item) {
            return (
              <ChatMessage key={item.id} role="assistant">
                <p className="error-text">{item.error}</p>
              </ChatMessage>
            );
          }

          return (
            <ChatMessage key={item.id} role="assistant">
              <div className="recipe-stack">
                {item.recipes.map((recipe, index) => (
                  <RecipeCard key={`${recipe.name}-${index}`} recipe={recipe} />
                ))}
              </div>
            </ChatMessage>
          );
        })}

        {loading && (
          <ChatMessage role="assistant">
            <div className="recipe-stack">
              <RecipeSkeleton />
              <RecipeSkeleton />
            </div>
          </ChatMessage>
        )}
      </section>

      <footer className="chat-footer">
        <ChatInput disabled={loading} onSend={handleSend} />
      </footer>
    </main>
  );
}
