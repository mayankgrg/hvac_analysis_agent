import Link from "next/link";

export type ProjectCardData = {
  project_id: string;
  project_name: string;
  health_score?: number;
  status?: "RED" | "YELLOW" | "GREEN";
  margin_erosion_pct?: number;
};

export function ProjectCard({ data, analyzed }: { data: ProjectCardData; analyzed: boolean }) {
  const statusClass = !analyzed
    ? ""
    : data.status === "RED"
      ? "bad"
      : data.status === "YELLOW"
        ? "warn"
        : "good";

  return (
    <div className="card">
      <div style={{ fontSize: 12, opacity: 0.7 }}>{data.project_id}</div>
      <h3 style={{ marginTop: 8 }}>{data.project_name}</h3>
      {analyzed ? (
        <>
          <p className={statusClass} style={{ fontWeight: 700, marginBottom: 6 }}>
            {data.status} | Health {data.health_score?.toFixed(1)}
          </p>
          <p style={{ marginTop: 0 }}>Margin erosion: {((data.margin_erosion_pct ?? 0) * 100).toFixed(1)}%</p>
          <Link className="btn" href={`/project/${data.project_id}`}>
            View Insights
          </Link>
        </>
      ) : (
        <p style={{ color: "var(--muted)" }}>Ready for real-time analysis.</p>
      )}
    </div>
  );
}
