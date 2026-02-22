from __future__ import annotations

import json
from fastapi import APIRouter, HTTPException

from backend.db.connection import get_connection

router = APIRouter(prefix="/api", tags=["dossier"])


@router.get("/dossier/{project_id}")
def get_dossier(project_id: str):
    conn = get_connection()
    try:
        row = conn.execute("SELECT dossier_json FROM dossiers WHERE project_id=?", (project_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Dossier not found for {project_id}")
        return json.loads(row[0])
    finally:
        conn.close()
