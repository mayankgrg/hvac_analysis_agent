from __future__ import annotations

import sqlite3


def compute_health_score(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT project_id, margin_erosion_pct, pending_co_exposure, contract_value,
               billing_lag, open_rfis, overdue_rfis, orphan_rfis, exceedance_lines, total_lines
        FROM computed_project_metrics
        """
    ).fetchall()

    for row in rows:
        (
            project_id,
            erosion,
            pending_co,
            contract,
            billing_lag,
            open_rfis,
            overdue_rfis,
            orphan_rfis,
            exceedance_lines,
            total_lines,
        ) = row

        score = 100.0
        erosion = float(erosion or 0)
        pending_pct = (float(pending_co or 0) / float(contract or 1)) if float(contract or 0) else 0.0
        billing_pct = (float(billing_lag or 0) / float(contract or 1)) if float(contract or 0) else 0.0
        exceedance_pct = (float(exceedance_lines or 0) / float(total_lines or 1))

        score -= min(40.0, max(0.0, erosion * 120.0))
        score -= min(20.0, max(0.0, pending_pct * 200.0))
        score -= min(20.0, max(0.0, billing_pct * 100.0))
        score -= min(10.0, float(overdue_rfis or 0) * 0.75)
        score -= min(8.0, float(orphan_rfis or 0) * 1.2)
        score -= min(12.0, exceedance_pct * 30.0)

        score = max(0.0, min(100.0, score))
        if score < 50:
            status = "RED"
        elif score < 80:
            status = "YELLOW"
        else:
            status = "GREEN"

        conn.execute(
            "UPDATE computed_project_metrics SET health_score=?, status=? WHERE project_id=?",
            (score, status, project_id),
        )
