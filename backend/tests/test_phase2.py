from __future__ import annotations

import sqlite3
from pathlib import Path
import unittest

from backend.compute import run_compute_engine
from backend.scripts.seed_db import seed_db

DB_PATH = Path(__file__).resolve().parents[1] / "hvac.db"


class TestPhase2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_db()
        run_compute_engine(DB_PATH)

    def test_manual_labor_formula(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute(
                "SELECT project_id, sov_line_id, hours_st, hours_ot, hourly_rate, burden_multiplier FROM labor_logs LIMIT 1"
            ).fetchone()
            project_id, sov_line_id, st, ot, rate, burden = row
            manual = (float(st) + 1.5 * float(ot)) * float(rate) * float(burden)
            total = conn.execute(
                "SELECT actual_labor_cost FROM computed_sov_metrics WHERE project_id=? AND sov_line_id=?",
                (project_id, sov_line_id),
            ).fetchone()[0]
            self.assertGreaterEqual(float(total), manual)
        finally:
            conn.close()

    def test_scores_range(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            rows = conn.execute("SELECT health_score FROM computed_project_metrics").fetchall()
            self.assertGreater(len(rows), 0)
            for (score,) in rows:
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
