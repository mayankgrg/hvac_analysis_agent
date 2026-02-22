from __future__ import annotations

import sqlite3


def compute_labor(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        UPDATE computed_sov_metrics
        SET actual_labor_cost = COALESCE((
          SELECT SUM((hours_st + (hours_ot*1.5)) * hourly_rate * burden_multiplier)
          FROM labor_logs l
          WHERE l.project_id = computed_sov_metrics.project_id
            AND l.sov_line_id = computed_sov_metrics.sov_line_id
        ), 0)
        """
    )
