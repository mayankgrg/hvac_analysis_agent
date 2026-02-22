from __future__ import annotations

import sqlite3


def compute_billing(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        UPDATE computed_sov_metrics
        SET billing_total = COALESCE((
          SELECT MAX(total_billed)
          FROM billing_line_items b
          WHERE b.project_id = computed_sov_metrics.project_id
            AND b.sov_line_id = computed_sov_metrics.sov_line_id
        ), 0)
        """
    )
    conn.execute(
        """
        UPDATE computed_sov_metrics
        SET billing_lag = (actual_labor_cost + actual_material_cost) - billing_total
        """
    )
