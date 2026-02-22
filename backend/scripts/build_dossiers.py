from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.compute import run_compute_engine
from backend.reasoning.dossier_builder import build_project_dossier
from backend.reasoning.portfolio_builder import build_portfolio
from backend.scripts.seed_db import seed_db

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "hvac.db"


def build_all() -> None:
    seed_db()
    run_compute_engine(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        projects = [r[0] for r in conn.execute("SELECT project_id FROM contracts").fetchall()]
        for project_id in projects:
            build_project_dossier(conn, project_id)
        build_portfolio(conn)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    build_all()
    print("Built dossiers and portfolio")
