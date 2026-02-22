from __future__ import annotations

import json
import sqlite3
from typing import Any


def build_portfolio(conn: sqlite3.Connection) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT project_id, project_name, health_score, status, bid_margin_pct, realized_margin_pct, margin_erosion_pct FROM computed_project_metrics ORDER BY health_score ASC"
    ).fetchall()
    projects = []
    for r in rows:
        projects.append(
            {
                "project_id": r[0],
                "project_name": r[1],
                "health_score": r[2],
                "status": r[3],
                "bid_margin_pct": r[4],
                "realized_margin_pct": r[5],
                "margin_erosion_pct": r[6],
            }
        )

    payload = {
        "headline": "Portfolio margin health summary",
        "project_count": len(projects),
        "projects": projects,
        "red_count": sum(1 for p in projects if p["status"] == "RED"),
    }

    conn.execute(
        "INSERT INTO dossiers(project_id, dossier_json) VALUES('PORTFOLIO', ?) ON CONFLICT(project_id) DO UPDATE SET dossier_json=excluded.dossier_json, updated_at=CURRENT_TIMESTAMP",
        (json.dumps(payload),),
    )
    return payload
