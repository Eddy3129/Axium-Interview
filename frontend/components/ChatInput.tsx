"use client";

import { useState } from "react";

interface ChatInputProps {
  disabled?: boolean;
  onSend: (value: string) => Promise<void> | void;
}

export default function ChatInput({
  disabled = false,
  onSend,
}: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = async () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    await onSend(trimmed);
    setValue("");
  };

  return (
    <div className="chat-input-wrap">
      <textarea
        className="chat-input"
        value={value}
        disabled={disabled}
        rows={2}
        placeholder="Type ingredients, e.g. chicken, garlic, lemon, pasta"
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            void handleSubmit();
          }
        }}
      />
      <button
        className="send-btn"
        disabled={disabled || !value.trim()}
        onClick={() => void handleSubmit()}
      >
        Send
      </button>
      <p className="input-hint">
        Press Enter to send. Use Shift+Enter for newline.
      </p>
    </div>
  );
}
