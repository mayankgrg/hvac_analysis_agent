"use client";

import { useState } from "react";
import { ReasoningPanel } from "./reasoning-panel";

export function IssueCard({ issue }: { issue: any }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="card" style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <strong>{issue.type}</strong> | {issue.severity}
          <div style={{ fontSize: 12, opacity: 0.7 }}>Value: {issue.value}</div>
        </div>
        <button className="btn" onClick={() => setOpen((v) => !v)}>
          {open ? "Hide Reasoning" : "View Reasoning"}
        </button>
      </div>
      {open ? <ReasoningPanel reasoning={issue.reasoning} /> : null}
    </div>
  );
}
