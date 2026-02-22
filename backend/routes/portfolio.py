from __future__ import annotations

import json
from fastapi import APIRouter, HTTPException

from backend.db.connection import get_connection

router = APIRouter(prefix="/api", tags=["portfolio"])


@router.get("/portfolio")
def get_portfolio():
    conn = get_connection()
    try:
        row = conn.execute("SELECT dossier_json FROM dossiers WHERE project_id='PORTFOLIO'").fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Portfolio dossier not built yet")
        return json.loads(row[0])
    finally:
        conn.close()
