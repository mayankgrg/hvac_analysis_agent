from __future__ import annotations

import json
from fastapi import APIRouter
from pydantic import BaseModel

from backend.db.connection import get_connection
from backend.tools.co_detail import get_co_detail
from backend.tools.field_notes import get_field_notes
from backend.tools.labor_detail import get_labor_detail
from backend.tools.rfi_detail import get_rfi_detail
from backend.tools.what_if_margin import what_if_margin

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    project_id: str
    message: str


@router.post("/chat")
def chat(req: ChatRequest):
    msg = req.message.lower().strip()
    conn = get_connection()
    try:
        dossier_row = conn.execute("SELECT dossier_json FROM dossiers WHERE project_id=?", (req.project_id,)).fetchone()
        if not dossier_row:
            return {"answer": "Run analysis first; dossier missing.", "tools": []}

        tools_used = []
        if "field note" in msg:
            tools_used.append("get_field_notes")
            notes = get_field_notes(conn, req.project_id, keyword="")
            return {"answer": f"Found {len(notes)} recent field notes.", "tools": tools_used, "data": notes[:5]}
        if "co-" in msg:
            token = next((w.upper().strip(".,") for w in req.message.split() if w.upper().startswith("CO-")), None)
            if token:
                tools_used.append("get_co_detail")
                return {"answer": f"Loaded details for {token}.", "tools": tools_used, "data": get_co_detail(conn, token)}
        if "rfi-" in msg:
            token = next((w.upper().strip(".,") for w in req.message.split() if w.upper().startswith("RFI-")), None)
            if token:
                tools_used.append("get_rfi_detail")
                return {"answer": f"Loaded details for {token}.", "tools": tools_used, "data": get_rfi_detail(conn, token)}
        if "what if" in msg or "recover" in msg:
            tools_used.append("what_if_margin")
            data = what_if_margin(conn, req.project_id, recovery_amount=250000)
            return {"answer": "Computed what-if margin with $250k recovery.", "tools": tools_used, "data": data}
        if "labor" in msg and "sov" in msg:
            parts = req.message.split()
            sov = next((p for p in parts if "SOV" in p.upper()), None)
            if sov:
                tools_used.append("get_labor_detail")
                return {"answer": f"Loaded labor detail for {sov}.", "tools": tools_used, "data": get_labor_detail(conn, req.project_id, sov)}

        dossier = json.loads(dossier_row[0])
        return {
            "answer": (
                f"{dossier['name']} is {dossier['status']} with health {dossier['health_score']:.1f}. "
                f"Margin erosion is {dossier['financials']['margin_erosion_pct']:.1%} with "
                f"{len(dossier['issues'])} active trigger(s)."
            ),
            "tools": tools_used,
        }
    finally:
        conn.close()
