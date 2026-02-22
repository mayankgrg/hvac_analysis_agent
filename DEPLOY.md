# Deployment Guide (GitHub + Backend + Vercel)

This project uses a two-service deployment:
- `frontend/` -> Vercel (Next.js + Vercel AI SDK route)
- `backend/` -> Render/Railway/Fly (FastAPI + SQLite + compute pipeline)

## 1) Push To GitHub

```bash
cd "/Users/mayankgarg/Documents/Pulse hackathon/Hackathon-5-main"

git remote add origin https://github.com/<your-user>/<your-repo>.git
# if remote already exists: git remote set-url origin https://github.com/<your-user>/<your-repo>.git

git push -u origin main
```

## 2) Deploy Backend (Render recommended)

Deploy backend from the same repo root.

### Render settings
- **Service type**: Web Service
- **Runtime**: Python
- **Root directory**: repo root (leave empty)
- **Build command**:

```bash
python -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r backend/requirements.txt && python -m backend.scripts.build_dossiers
```

- **Start command**:

```bash
source .venv/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

- **Health check path**: `/health`

### Backend env vars (optional email SMTP)
Use only if you want real outbound emails (otherwise it logs to `backend/email_log.jsonl`).

- `SMTP_HOST`
- `SMTP_PORT` (default `587`)
- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_FROM`

After deploy, copy backend URL, e.g.:
- `https://hvac-margin-backend.onrender.com`

## 3) Deploy Frontend On Vercel

### Vercel project setup
- Import your GitHub repo
- **Framework**: Next.js
- **Root Directory**: `frontend`
- Build command: `npm run build`
- Install command: `npm install`

### Frontend env vars (required)
- `OPENAI_API_KEY=<your-openai-key>`
- `BACKEND_URL=https://<your-backend-url>`
- `NEXT_PUBLIC_BACKEND_URL=https://<your-backend-url>`

`BACKEND_URL` is used by server routes (`frontend/app/api/chat/route.ts`).
`NEXT_PUBLIC_BACKEND_URL` is used by client-side fetches.

## 4) Post-Deploy Smoke Tests

Run these against deployed backend:

```bash
curl https://<backend-url>/health
curl https://<backend-url>/api/portfolio
curl https://<backend-url>/api/dossier/PRJ-2024-001
curl -X POST https://<backend-url>/api/tools/what-if-margin \
  -H "Content-Type: application/json" \
  -d '{"project_id":"PRJ-2024-001","recovery_amount":250000}'
```

From the Vercel frontend URL:
1. Open app landing page
2. Click `Run Real-Time Analysis`
3. Open a project via `View Insights`
4. Expand `View Reasoning`
5. Ask in chat: `What are top recovery actions for this project?`
6. Ask in chat: `What if we recover $250,000?`

## 5) Scoring Alignment Checklist (README.md)

### Agent Intelligence (40)
- Agent route uses Vercel AI SDK tools (`frontend/app/api/chat/route.ts`)
- Multi-step autonomy enabled: `stopWhen: stepCountIs(8)`
- Tool-backed answers against backend dossier + detail endpoints

### Agent Experience (30)
- Chat UI supports ongoing conversation context (`frontend/components/chat-panel.tsx`)
- Route streams via AI SDK data stream response
- Reasoning details visible in dossier issue cards

### Implementation Quality (20)
- v0-compatible component structure in `frontend/components/*`
- Vercel AI SDK integrated in API route
- Granola-style instruction profile in `frontend/lib/granola.ts`
- Email tool available (`/api/email` + `sendEmail` tool)

### Business Insight (10)
- Dossiers include root cause, contributing factors, recovery actions, recoverable amounts
- What-if margin tool quantifies recovery scenarios

## 6) Common Issues

### `OPENAI_API_KEY is missing`
Set env var in Vercel project settings and redeploy.

### Frontend loads but API calls fail
Verify both `BACKEND_URL` and `NEXT_PUBLIC_BACKEND_URL` point to the same live backend.

### Backend 500 on first run
Ensure build command runs:

```bash
python -m backend.scripts.build_dossiers
```

This seeds DB + computes metrics + builds dossiers.

### Email not delivered
Without SMTP env vars, email calls are logged locally by design.

## 7) Optional: Local Verification Before Deploy

```bash
# backend
python3 -m backend.scripts.build_dossiers
python3 backend/tests/run_tests.py
uvicorn backend.main:app --reload --port 8000

# frontend
cd frontend
npm install
BACKEND_URL=http://localhost:8000 NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 npm run dev
```
