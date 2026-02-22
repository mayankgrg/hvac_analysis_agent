from __future__ import annotations

import sqlite3


def get_labor_detail(conn: sqlite3.Connection, project_id: str, sov_line_id: str):
    rows = conn.execute(
        "SELECT date, role, hours_st, hours_ot, hourly_rate, burden_multiplier FROM labor_logs WHERE project_id=? AND sov_line_id=? ORDER BY date DESC LIMIT 200",
        (project_id, sov_line_id),
    ).fetchall()
    total = 0.0
    for r in rows:
        total += (float(r[2]) + 1.5 * float(r[3])) * float(r[4]) * float(r[5])
    return {"rows": [dict(r) for r in rows], "computed_cost": total}
