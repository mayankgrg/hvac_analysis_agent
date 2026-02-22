from __future__ import annotations

import sqlite3


def what_if_margin(conn: sqlite3.Connection, project_id: str, recovery_amount: float):
    row = conn.execute(
        "SELECT contract_value, total_actual_cost, realized_margin_pct FROM computed_project_metrics WHERE project_id=?",
        (project_id,),
    ).fetchone()
    if not row:
        return None
    contract, actual, current = map(float, row)
    new_actual = max(0.0, actual - recovery_amount)
    new_margin = (contract - new_actual) / contract if contract else 0.0
    return {
        "project_id": project_id,
        "current_realized_margin_pct": current,
        "new_realized_margin_pct": new_margin,
        "delta_margin_pct": new_margin - current,
        "recovery_amount": recovery_amount,
    }
