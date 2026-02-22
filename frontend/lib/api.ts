export const backendBase =
  process.env.BACKEND_URL ??
  process.env.NEXT_PUBLIC_BACKEND_URL ??
  "http://localhost:8000";

export async function getPortfolio() {
  const r = await fetch(`${backendBase}/api/portfolio`, { cache: "no-store" });
  if (!r.ok) throw new Error("Failed portfolio fetch");
  return r.json();
}

export async function getDossier(projectId: string) {
  const r = await fetch(`${backendBase}/api/dossier/${projectId}`, { cache: "no-store" });
  if (!r.ok) throw new Error(`Failed dossier fetch ${projectId}`);
  return r.json();
}
