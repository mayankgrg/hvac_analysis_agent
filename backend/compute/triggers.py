from __future__ import annotations

import json
import sqlite3


def _sev(value: float, threshold: float) -> str:
    ratio = (value / threshold) if threshold else 0.0
    if ratio >= 2:
        return "HIGH"
    if ratio >= 1.25:
        return "MEDIUM"
    return "LOW"


def compute_triggers(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM triggers")
    projects = conn.execute("SELECT * FROM computed_project_metrics").fetchall()

    for p in projects:
        project_id = p[0]
        trigger_idx = 1

        # labor overrun per line
        lines = conn.execute(
            "SELECT sov_line_id, overrun_pct, overrun_amount FROM computed_sov_metrics WHERE project_id=?",
            (project_id,),
        ).fetchall()
        for sov_line_id, overrun_pct, overrun_amount in lines:
            val = float(overrun_pct or 0)
            if val > 0.15:
                conn.execute(
                    "INSERT INTO triggers(trigger_id, project_id, date, type, severity, value, threshold, details, affected_sov_lines) VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        f"{project_id}-TRG-{trigger_idx:03d}",
                        project_id,
                        "2025-01-01",
                        "LINE_OVERRUN",
                        _sev(val, 0.15),
                        val,
                        0.15,
                        json.dumps({"overrun_amount": overrun_amount}),
                        json.dumps([sov_line_id]),
                    ),
                )
                trigger_idx += 1

        pending_pct = (float(p[10] or 0) / float(p[2] or 1)) if float(p[2] or 0) else 0
        if pending_pct > 0.05:
            conn.execute(
                "INSERT INTO triggers(trigger_id, project_id, date, type, severity, value, threshold, details, affected_sov_lines) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    f"{project_id}-TRG-{trigger_idx:03d}",
                    project_id,
                    "2025-01-15",
                    "PENDING_CO_EXPOSURE",
                    _sev(pending_pct, 0.05),
                    pending_pct,
                    0.05,
                    json.dumps({"pending_co_exposure": p[10]}),
                    "[]",
                ),
            )
            trigger_idx += 1

        billing_pct = (float(p[13] or 0) / float(p[2] or 1)) if float(p[2] or 0) else 0
        if billing_pct > 0.03:
            conn.execute(
                "INSERT INTO triggers(trigger_id, project_id, date, type, severity, value, threshold, details, affected_sov_lines) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    f"{project_id}-TRG-{trigger_idx:03d}",
                    project_id,
                    "2025-02-01",
                    "BILLING_LAG",
                    _sev(billing_pct, 0.03),
                    billing_pct,
                    0.03,
                    json.dumps({"billing_lag": p[13]}),
                    "[]",
                ),
            )
            trigger_idx += 1

        if int(p[16] or 0) > 0:
            conn.execute(
                "INSERT INTO triggers(trigger_id, project_id, date, type, severity, value, threshold, details, affected_sov_lines) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    f"{project_id}-TRG-{trigger_idx:03d}",
                    project_id,
                    "2025-02-10",
                    "ORPHAN_RFI",
                    _sev(float(p[16]), 1.0),
                    float(p[16]),
                    1.0,
                    json.dumps({"orphan_rfis": p[16]}),
                    "[]",
                ),
            )
