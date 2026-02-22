from __future__ import annotations

import sqlite3


def compute_rfi_metrics(conn: sqlite3.Connection) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    projects = [r[0] for r in conn.execute("SELECT project_id FROM contracts").fetchall()]
    for p in projects:
        open_count = conn.execute(
            "SELECT COUNT(*) FROM rfis WHERE project_id=? AND status != 'Closed'", (p,)
        ).fetchone()[0]
        overdue_count = conn.execute(
            "SELECT COUNT(*) FROM rfis WHERE project_id=? AND status != 'Closed' AND date_required < DATE('now')",
            (p,),
        ).fetchone()[0]
        orphan_count = conn.execute(
            """
            SELECT COUNT(*) FROM rfis r
            WHERE r.project_id=?
              AND LOWER(COALESCE(r.cost_impact, '')) IN ('true','1','yes')
              AND NOT EXISTS (
                SELECT 1 FROM change_orders c
                WHERE c.project_id=r.project_id AND c.related_rfi=r.rfi_number
              )
            """,
            (p,),
        ).fetchone()[0]
        out[p] = {"open_rfis": open_count, "overdue_rfis": overdue_count, "orphan_rfis": orphan_count}
    return out
