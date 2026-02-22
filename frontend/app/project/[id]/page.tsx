import Link from "next/link";
import { DossierHeader } from "@/components/dossier-header";
import { IssueCard } from "@/components/issue-card";
import { ChatPanel } from "@/components/chat-panel";

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const r = await fetch(`${base}/api/dossier/${params.id}`, { cache: "no-store" });
  if (!r.ok) {
    return <main className="container"><p>Dossier not found for {params.id}</p><Link href="/">Back</Link></main>;
  }

  const dossier = await r.json();
  return (
    <main className="container">
      <Link href="/">Back to Portfolio</Link>
      <DossierHeader dossier={dossier} />
      <h3>Issues</h3>
      {dossier.issues.map((issue: any) => (
        <IssueCard key={issue.trigger_id} issue={issue} />
      ))}
      <ChatPanel projectId={params.id} />
    </main>
  );
}
