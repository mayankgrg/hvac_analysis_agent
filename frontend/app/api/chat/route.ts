import { backendBase } from "@/lib/api";
import { granolaInstruction } from "@/lib/granola";
import { openai } from "@ai-sdk/openai";
import { stepCountIs, streamText, tool } from "ai";
import { z } from "zod";

function fail(message: string, status = 500) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { "content-type": "application/json" }
  });
}

export const maxDuration = 60;

export async function POST(req: Request) {
  if (!process.env.OPENAI_API_KEY) {
    return fail("OPENAI_API_KEY is missing");
  }

  const body = await req.json();
  const messages = body.messages ?? [];
  const projectId = body.projectId;

  if (!projectId) {
    return fail("projectId is required", 400);
  }

  const system = [
    `You are ${granolaInstruction.name}.`,
    "Primary mission: autonomously protect margin across HVAC projects.",
    "Operate in a scan -> investigate -> act -> converse loop.",
    "Use tools to ground every claim in project data and never invent IDs or amounts.",
    "When user asks a narrow follow-up, still check if another tool call is needed before final answer.",
    "Return clear actions with owner, urgency, and dollar impact whenever possible.",
    "Granola goals:",
    ...granolaInstruction.goals.map((g) => `- ${g}`),
    `Communication style: ${granolaInstruction.style}`
  ].join("\n");

  const result = streamText({
    model: openai("gpt-4o-mini"),
    system,
    messages,
    stopWhen: stepCountIs(8),
    onStepFinish(step) {
      console.log("agent-step", {
        finishReason: step.finishReason,
        toolCalls: step.toolCalls?.length ?? 0,
        textLength: step.text?.length ?? 0
      });
    },
    tools: {
      getPortfolio: tool({
        description: "Load current portfolio summary and project health states.",
        inputSchema: z.object({}),
        execute: async () => {
          const res = await fetch(`${backendBase}/api/portfolio`, { cache: "no-store" });
          if (!res.ok) throw new Error("Failed to load portfolio");
          return res.json();
        }
      }),
      getDossier: tool({
        description: "Load detailed dossier for a project including financials and issues.",
        inputSchema: z.object({ projectId: z.string() }),
        execute: async ({ projectId }) => {
          const res = await fetch(`${backendBase}/api/dossier/${projectId}`, { cache: "no-store" });
          if (!res.ok) throw new Error(`Failed to load dossier for ${projectId}`);
          return res.json();
        }
      }),
      getFieldNotes: tool({
        description: "Search field notes for a project by keyword.",
        inputSchema: z.object({
          projectId: z.string(),
          keyword: z.string().default(""),
          limit: z.number().min(1).max(100).default(20)
        }),
        execute: async ({ projectId, keyword, limit }) => {
          const res = await fetch(`${backendBase}/api/tools/field-notes`, {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ project_id: projectId, keyword, limit })
          });
          if (!res.ok) throw new Error("Failed to fetch field notes");
          return res.json();
        }
      }),
      getLaborDetail: tool({
        description: "Fetch detailed labor logs and computed labor cost for a project SOV line.",
        inputSchema: z.object({
          projectId: z.string(),
          sovLineId: z.string()
        }),
        execute: async ({ projectId, sovLineId }) => {
          const res = await fetch(`${backendBase}/api/tools/labor-detail`, {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ project_id: projectId, sov_line_id: sovLineId })
          });
          if (!res.ok) throw new Error("Failed to fetch labor detail");
          return res.json();
        }
      }),
      getChangeOrderDetail: tool({
        description: "Fetch one change order detail by CO number.",
        inputSchema: z.object({
          projectId: z.string(),
          coNumber: z.string()
        }),
        execute: async ({ projectId, coNumber }) => {
          const res = await fetch(`${backendBase}/api/tools/co-detail`, {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ project_id: projectId, co_number: coNumber })
          });
          if (!res.ok) throw new Error(`CO ${coNumber} not found`);
          return res.json();
        }
      }),
      getRfiDetail: tool({
        description: "Fetch one RFI detail by RFI number.",
        inputSchema: z.object({
          projectId: z.string(),
          rfiNumber: z.string()
        }),
        execute: async ({ projectId, rfiNumber }) => {
          const res = await fetch(`${backendBase}/api/tools/rfi-detail`, {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ project_id: projectId, rfi_number: rfiNumber })
          });
          if (!res.ok) throw new Error(`RFI ${rfiNumber} not found`);
          return res.json();
        }
      }),
      whatIfMargin: tool({
        description: "Run margin impact scenario for a given project and recoverable amount.",
        inputSchema: z.object({
          projectId: z.string(),
          recoveryAmount: z.number().min(0)
        }),
        execute: async ({ projectId, recoveryAmount }) => {
          const res = await fetch(`${backendBase}/api/tools/what-if-margin`, {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ project_id: projectId, recovery_amount: recoveryAmount })
          });
          if (!res.ok) throw new Error("Failed what-if margin computation");
          return res.json();
        }
      }),
      sendEmail: tool({
        description: "Send a project summary or escalation email.",
        inputSchema: z.object({
          to: z.string().email(),
          subject: z.string().min(3),
          body: z.string().min(5)
        }),
        execute: async ({ to, subject, body }) => {
          const res = await fetch(`${backendBase}/api/email`, {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ to, subject, body })
          });
          if (!res.ok) throw new Error("Failed to send email");
          return res.json();
        }
      }),
      getCurrentProjectDossier: tool({
        description: "Load dossier for the currently active project in chat.",
        inputSchema: z.object({}),
        execute: async () => {
          const res = await fetch(`${backendBase}/api/dossier/${projectId}`, { cache: "no-store" });
          if (!res.ok) throw new Error(`Failed to load current project dossier ${projectId}`);
          return res.json();
        }
      })
    }
  });

  return result.toDataStreamResponse();
}
