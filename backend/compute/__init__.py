from __future__ import annotations

import sqlite3
from pathlib import Path

from .billing import compute_billing
from .financials import compute_project_financials, finalize_sov_metrics, initialize_sov_metrics
from .health_score import compute_health_score
from .labor import compute_labor
from .materials import compute_materials
from .rfis import compute_rfi_metrics
from .triggers import compute_triggers


def run_compute_engine(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        initialize_sov_metrics(conn)
        compute_labor(conn)
        compute_materials(conn)
        compute_billing(conn)
        finalize_sov_metrics(conn)
        rfi_metrics = compute_rfi_metrics(conn)
        compute_project_financials(conn, rfi_metrics)
        compute_health_score(conn)
        compute_triggers(conn)
        conn.commit()
    finally:
        conn.close()
