"use client";

import { useState } from "react";
import { backendBase } from "@/lib/api";
import { granolaInstruction } from "@/lib/granola";

export function ChatPanel({ projectId }: { projectId: string }) {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function ask() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${backendBase}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId, message: `[${granolaInstruction.name}] ${q}` })
      });
      const data = await res.json();
      setAnswer(data.answer ?? "No response");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown chat error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card" style={{ marginTop: 12 }}>
      <h3 style={{ marginTop: 0 }}>Agent Chat</h3>
      <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 8 }}>
        Granola prompt profile active: {granolaInstruction.name}
      </div>

      <textarea
        value={q}
        onChange={(e) => setQ(e.target.value)}
        rows={3}
        style={{ width: "100%", marginBottom: 8 }}
        placeholder="Example: What are top recovery actions and what is the $ impact?"
      />
      <button className="btn btn-primary" onClick={ask} disabled={loading}>
        {loading ? "Thinking..." : "Ask Agent"}
      </button>

      {error ? <p className="bad" style={{ marginBottom: 0 }}>Chat error: {error}</p> : null}
      {answer ? <p style={{ marginBottom: 0 }}>{answer}</p> : null}
    </div>
  );
}
