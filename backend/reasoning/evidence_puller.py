from __future__ import annotations

import json
import sqlite3
from typing import Any


def pull_evidence_for_trigger(conn: sqlite3.Connection, trigger_id: str) -> dict[str, Any]:
    t = conn.execute("SELECT * FROM triggers WHERE trigger_id=?", (trigger_id,)).fetchone()
    if not t:
        return {}
    project_id = t[1]
    affected = json.loads(t[8] or "[]")

    notes = conn.execute(
        "SELECT note_id, date, note_type, content FROM field_notes WHERE project_id=? ORDER BY date DESC LIMIT 15",
        (project_id,),
    ).fetchall()
    co_rows = conn.execute(
        "SELECT co_number, date_submitted, amount, status, description FROM change_orders WHERE project_id=? ORDER BY date_submitted DESC LIMIT 10",
        (project_id,),
    ).fetchall()
    rfi_rows = conn.execute(
        "SELECT rfi_number, priority, status, subject FROM rfis WHERE project_id=? ORDER BY date_submitted DESC LIMIT 10",
        (project_id,),
    ).fetchall()
    if affected:
        q_marks = ",".join(["?"] * len(affected))
        labor = conn.execute(
            f"SELECT date, sov_line_id, hours_st, hours_ot, hourly_rate FROM labor_logs WHERE project_id=? AND sov_line_id IN ({q_marks}) LIMIT 50",
            (project_id, *affected),
        ).fetchall()
    else:
        labor = conn.execute(
            "SELECT date, sov_line_id, hours_st, hours_ot, hourly_rate FROM labor_logs WHERE project_id=? LIMIT 50",
            (project_id,),
        ).fetchall()

    return {
        "trigger_id": trigger_id,
        "project_id": project_id,
        "trigger_type": t[3],
        "trigger_value": t[5],
        "affected_sov_lines": affected,
        "field_notes": [dict(x) for x in notes],
        "change_orders": [dict(x) for x in co_rows],
        "rfis": [dict(x) for x in rfi_rows],
        "labor_samples": [dict(x) for x in labor],
    }
