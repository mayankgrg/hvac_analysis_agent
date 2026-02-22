from __future__ import annotations

import ast
import sqlite3


def _rejected_co_exposure_by_line(conn: sqlite3.Connection) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    rows = conn.execute(
        "SELECT project_id, amount, affected_sov_lines FROM change_orders WHERE status='Rejected'"
    ).fetchall()
    for project_id, amount, affected in rows:
        amt = float(amount or 0)
        if amt <= 0:
            continue
        try:
            lines = ast.literal_eval(affected or "[]")
            if not isinstance(lines, list):
                lines = []
        except Exception:
            lines = []
        if not lines:
            continue
        piece = amt / len(lines)
        for line in lines:
            out[(project_id, line)] = out.get((project_id, line), 0.0) + piece
    return out


def initialize_sov_metrics(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM computed_sov_metrics")
    conn.execute(
        """
        INSERT INTO computed_sov_metrics (
          project_id, sov_line_id, line_number, description, scheduled_value,
          estimated_labor_cost, estimated_material_cost, estimated_equipment_cost,
          estimated_sub_cost, bid_max_cost,
          actual_labor_cost, actual_material_cost, billing_total, billing_lag,
          rejected_co_exposure, labor_overrun_pct, material_variance_pct,
          overrun_amount, overrun_pct
        )
        SELECT
          s.project_id,
          s.sov_line_id,
          s.line_number,
          s.description,
          COALESCE(s.scheduled_value, 0),
          COALESCE(b.estimated_labor_cost, 0),
          COALESCE(b.estimated_material_cost, 0),
          COALESCE(b.estimated_equipment_cost, 0),
          COALESCE(b.estimated_sub_cost, 0),
          COALESCE(b.estimated_labor_cost, 0) + COALESCE(b.estimated_material_cost, 0)
            + COALESCE(b.estimated_equipment_cost, 0) + COALESCE(b.estimated_sub_cost, 0),
          0, 0, 0, 0,
          0, 0, 0, 0, 0
        FROM sov s
        LEFT JOIN sov_budget b ON s.sov_line_id = b.sov_line_id
        """
    )


def finalize_sov_metrics(conn: sqlite3.Connection) -> None:
    exposure = _rejected_co_exposure_by_line(conn)
    for (project_id, sov_line_id), val in exposure.items():
        conn.execute(
            "UPDATE computed_sov_metrics SET rejected_co_exposure=? WHERE project_id=? AND sov_line_id=?",
            (val, project_id, sov_line_id),
        )

    conn.execute(
        """
        UPDATE computed_sov_metrics
        SET labor_overrun_pct = CASE
          WHEN estimated_labor_cost > 0 THEN (actual_labor_cost - estimated_labor_cost) / estimated_labor_cost
          ELSE 0 END,
            material_variance_pct = CASE
          WHEN estimated_material_cost > 0 THEN (actual_material_cost - estimated_material_cost) / estimated_material_cost
          ELSE 0 END,
            overrun_amount = (actual_labor_cost + actual_material_cost + rejected_co_exposure) - bid_max_cost,
            overrun_pct = CASE
          WHEN bid_max_cost > 0 THEN ((actual_labor_cost + actual_material_cost + rejected_co_exposure) - bid_max_cost)/bid_max_cost
          ELSE 0 END
        """
    )


def compute_project_financials(conn: sqlite3.Connection, rfi_metrics: dict[str, dict[str, int]]) -> None:
    conn.execute("DELETE FROM computed_project_metrics")
    projects = conn.execute(
        "SELECT project_id, project_name, original_contract_value FROM contracts"
    ).fetchall()

    for project_id, project_name, contract_value in projects:
        sum_row = conn.execute(
            """
            SELECT
              COALESCE(SUM(estimated_labor_cost + estimated_material_cost + estimated_equipment_cost + estimated_sub_cost), 0),
              COALESCE(SUM(actual_labor_cost), 0),
              COALESCE(SUM(actual_material_cost), 0),
              COALESCE(SUM(billing_lag), 0),
              COALESCE(SUM(CASE WHEN overrun_amount > 0 THEN 1 ELSE 0 END),0),
              COUNT(*)
            FROM computed_sov_metrics
            WHERE project_id=?
            """,
            (project_id,),
        ).fetchone()
        estimated_cost, actual_labor, actual_mat, billing_lag, exceeding_lines, total_lines = [float(x or 0) for x in sum_row]

        pending_co = float(
            conn.execute(
                "SELECT COALESCE(SUM(amount),0) FROM change_orders WHERE project_id=? AND status='Pending'",
                (project_id,),
            ).fetchone()[0]
            or 0
        )
        approved_co = float(
            conn.execute(
                "SELECT COALESCE(SUM(amount),0) FROM change_orders WHERE project_id=? AND status='Approved'",
                (project_id,),
            ).fetchone()[0]
            or 0
        )
        rejected_co = float(
            conn.execute(
                "SELECT COALESCE(SUM(amount),0) FROM change_orders WHERE project_id=? AND status='Rejected'",
                (project_id,),
            ).fetchone()[0]
            or 0
        )

        actual_total = actual_labor + actual_mat
        contract_value = float(contract_value or 0)
        bid_margin = (contract_value - estimated_cost) / contract_value if contract_value else 0.0
        realized_margin = (contract_value - actual_total) / contract_value if contract_value else 0.0
        erosion = bid_margin - realized_margin

        m = rfi_metrics.get(project_id, {"open_rfis": 0, "overdue_rfis": 0, "orphan_rfis": 0})

        conn.execute(
            """
            INSERT INTO computed_project_metrics (
              project_id, project_name, contract_value, total_estimated_cost,
              total_actual_labor_cost, total_actual_material_cost, total_actual_cost,
              bid_margin_pct, realized_margin_pct, margin_erosion_pct,
              pending_co_exposure, approved_co_total, rejected_co_total,
              billing_lag, open_rfis, overdue_rfis, orphan_rfis,
              health_score, status, exceedance_lines, total_lines
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'UNKNOWN', ?, ?)
            """,
            (
                project_id,
                project_name,
                contract_value,
                estimated_cost,
                actual_labor,
                actual_mat,
                actual_total,
                bid_margin,
                realized_margin,
                erosion,
                pending_co,
                approved_co,
                rejected_co,
                billing_lag,
                int(m["open_rfis"]),
                int(m["overdue_rfis"]),
                int(m["orphan_rfis"]),
                int(exceeding_lines),
                int(total_lines),
            ),
        )
