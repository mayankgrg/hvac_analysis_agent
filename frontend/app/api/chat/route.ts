import { backendBase } from "@/lib/api";

export async function POST(req: Request) {
  const body = await req.json();
  const projectId = body.projectId;
  const messages = body.messages ?? [];
  const last = messages[messages.length - 1]?.content ?? "";

  if (!projectId) {
    return new Response(JSON.stringify({ error: "projectId is required" }), {
      status: 400,
      headers: { "content-type": "application/json" }
    });
  }

  const res = await fetch(`${backendBase}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ project_id: projectId, message: last })
  });

  const json = await res.json();
  return new Response(JSON.stringify(json), {
    status: res.status,
    headers: { "content-type": "application/json" }
  });
}
