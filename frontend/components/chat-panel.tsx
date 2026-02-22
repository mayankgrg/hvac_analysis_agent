"use client";

import { useChat } from "ai/react";
import { granolaInstruction } from "@/lib/granola";

export function ChatPanel({ projectId }: { projectId: string }) {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: "/api/chat",
    body: { projectId }
  });

  return (
    <div className="card" style={{ marginTop: 12 }}>
      <h3 style={{ marginTop: 0 }}>Agent Chat</h3>
      <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 8 }}>
        Granola prompt profile active: {granolaInstruction.name}
      </div>

      <div
        style={{
          maxHeight: 240,
          overflowY: "auto",
          border: "1px solid var(--line)",
          borderRadius: 10,
          padding: 8,
          marginBottom: 8
        }}
      >
        {messages.length === 0 ? (
          <p style={{ margin: 0, opacity: 0.7 }}>Ask about risk, root cause, what-if margin, or send-email actions.</p>
        ) : null}
        {messages.map((m) => (
          <div key={m.id} style={{ marginBottom: 8 }}>
            <strong style={{ textTransform: "capitalize" }}>{m.role}:</strong>{" "}
            <span>{m.content}</span>
          </div>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit(e);
        }}
      >
        <textarea
          value={input}
          onChange={handleInputChange}
          rows={3}
          style={{ width: "100%", marginBottom: 8 }}
          placeholder="Example: What are the top 3 recovery actions and draft an email to the PM?"
        />
        <button className="btn btn-primary" type="submit" disabled={isLoading}>
          {isLoading ? "Thinking..." : "Ask Agent"}
        </button>
      </form>

      {error ? <p className="bad" style={{ marginBottom: 0 }}>Chat error: {error.message}</p> : null}
    </div>
  );
}
