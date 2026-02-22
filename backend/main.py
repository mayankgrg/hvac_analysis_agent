from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.chat import router as chat_router
from backend.routes.dossier import router as dossier_router
from backend.routes.email import router as email_router
from backend.routes.portfolio import router as portfolio_router
from backend.routes.tools import router as tools_router

app = FastAPI(title="HVAC Margin Rescue Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(portfolio_router)
app.include_router(dossier_router)
app.include_router(chat_router)
app.include_router(email_router)
app.include_router(tools_router)
