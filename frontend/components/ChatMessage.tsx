import { ReactNode } from "react";

interface ChatMessageProps {
  role: "user" | "assistant";
  children: ReactNode;
}

export default function ChatMessage({ role, children }: ChatMessageProps) {
  return (
    <div
      className={`message-row ${role === "user" ? "row-user" : "row-assistant"}`}
    >
      <div
        className={`message-bubble ${role === "user" ? "bubble-user" : "bubble-assistant"}`}
      >
        {children}
      </div>
    </div>
  );
}
