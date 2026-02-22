from __future__ import annotations

import json
import sqlite3
from typing import Any

from .evidence_puller import pull_evidence_for_trigger
from .reasoning_engine import generate_reasoning_from_evidence


def build_project_dossier(conn: sqlite3.Connection, project_id: str) -> dict[str, Any]:
    p = conn.execute("SELECT * FROM computed_project_metrics WHERE project_id=?", (project_id,)).fetchone()
    if not p:
        return {}

    trigger_rows = conn.execute("SELECT * FROM triggers WHERE project_id=? ORDER BY date", (project_id,)).fetchall()
    trigger_payload = []
    for t in trigger_rows:
        evidence = pull_evidence_for_trigger(conn, t[0])
        reasoning = generate_reasoning_from_evidence(evidence)
        trigger_payload.append(
            {
                "trigger_id": t[0],
                "date": t[2],
                "type": t[3],
                "severity": t[4],
                "value": t[5],
                "threshold": t[6],
                "details": json.loads(t[7] or "{}"),
                "affected_sov_lines": json.loads(t[8] or "[]"),
                "evidence": evidence,
                "reasoning": reasoning,
            }
        )

    dossier = {
        "project_id": p[0],
        "name": p[1],
        "health_score": p[17],
        "status": p[18],
        "financials": {
            "contract_value": p[2],
            "bid_margin_pct": p[7],
            "realized_margin_pct": p[8],
            "margin_erosion_pct": p[9],
            "pending_co_exposure": p[10],
            "billing_lag": p[13],
            "estimated_cost": p[3],
            "actual_cost": p[6],
        },
        "issues": trigger_payload,
        "summary": {
            "open_rfis": p[14],
            "overdue_rfis": p[15],
            "orphan_rfis": p[16],
            "exceedance_lines": p[19],
            "total_lines": p[20],
        },
    }

    conn.execute(
        "INSERT INTO dossiers(project_id, dossier_json) VALUES(?, ?) ON CONFLICT(project_id) DO UPDATE SET dossier_json=excluded.dossier_json, updated_at=CURRENT_TIMESTAMP",
        (project_id, json.dumps(dossier)),
    )
    return dossier
