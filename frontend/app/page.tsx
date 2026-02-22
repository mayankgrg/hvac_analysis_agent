"use client";

import { useMemo, useState } from "react";
import { PortfolioGrid } from "@/components/portfolio-grid";
import { ChatPanel } from "@/components/chat-panel";

const coldProjects = [
  { project_id: "PRJ-2024-001", project_name: "Mercy General Hospital - HVAC Modernization" },
  { project_id: "PRJ-2024-002", project_name: "Riverside Office Tower - Core & Shell MEP" },
  { project_id: "PRJ-2024-003", project_name: "Greenfield Elementary School - New Construction" },
  { project_id: "PRJ-2024-004", project_name: "Summit Data Center - Phase 2 Expansion" },
  { project_id: "PRJ-2024-005", project_name: "Harbor View Condominiums - 3 Buildings" }
];

export default function HomePage() {
  const [analyzed, setAnalyzed] = useState(false);
  const [projects, setProjects] = useState<any[]>(coldProjects);

  const redCount = useMemo(() => projects.filter((p) => p.status === "RED").length, [projects]);

  async function runAnalysis() {
    const r = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000"}/api/portfolio`);
    const data = await r.json();
    setProjects(data.projects || []);
    setAnalyzed(true);
  }

  return (
    <main className="container">
      <h1>HVAC Margin Rescue Agent</h1>
      <p>Two-step flow: red flag portfolio projects first, then dig deeper into root cause and actions.</p>
      <button className="btn btn-primary" onClick={runAnalysis}>Run Real-Time Analysis</button>
      {analyzed ? <p>RED projects: {redCount}</p> : null}
      <PortfolioGrid projects={projects} analyzed={analyzed} />
      <ChatPanel projectId={projects[0]?.project_id ?? "PRJ-2024-001"} />
    </main>
  );
}
