from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import unittest

from backend.reasoning.dossier_builder import build_project_dossier
from backend.reasoning.portfolio_builder import build_portfolio
from backend.scripts.seed_db import seed_db
from backend.compute import run_compute_engine

DB_PATH = Path(__file__).resolve().parents[1] / "hvac.db"


class TestPhase3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_db()
        run_compute_engine(DB_PATH)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            projects = [r[0] for r in conn.execute("SELECT project_id FROM contracts").fetchall()]
            for p in projects:
                build_project_dossier(conn, p)
            build_portfolio(conn)
            conn.commit()
        finally:
            conn.close()

    def test_dossiers_created(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            count = conn.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0]
            self.assertGreaterEqual(count, 6)
        finally:
            conn.close()

    def test_reasoning_shape(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute("SELECT dossier_json FROM dossiers WHERE project_id != 'PORTFOLIO' LIMIT 1").fetchone()
            d = json.loads(row[0])
            self.assertIn("issues", d)
            if d["issues"]:
                r = d["issues"][0]["reasoning"]
                for k in ["root_cause", "contributing_factors", "recovery_actions", "recoverable_amount", "confidence"]:
                    self.assertIn(k, r)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
