from __future__ import annotations

import sqlite3


def compute_materials(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        UPDATE computed_sov_metrics
        SET actual_material_cost = COALESCE((
          SELECT SUM(total_cost)
          FROM material_deliveries m
          WHERE m.project_id = computed_sov_metrics.project_id
            AND m.sov_line_id = computed_sov_metrics.sov_line_id
        ), 0)
        """
    )
