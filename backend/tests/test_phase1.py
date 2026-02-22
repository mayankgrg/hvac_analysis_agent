from __future__ import annotations

import sqlite3
from pathlib import Path
import unittest

from backend.scripts.seed_db import seed_db

DB_PATH = Path(__file__).resolve().parents[1] / "hvac.db"


class TestPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_db()

    def test_row_counts(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            tables = [
                "contracts",
                "sov",
                "sov_budget",
                "labor_logs",
                "material_deliveries",
                "billing_history",
                "billing_line_items",
                "change_orders",
                "rfis",
                "field_notes",
            ]
            for t in tables:
                c = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                self.assertGreater(c, 0, t)
        finally:
            conn.close()

    def test_foreign_keys_by_join(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            missing_labor_projects = conn.execute(
                "SELECT COUNT(*) FROM labor_logs l LEFT JOIN contracts c ON c.project_id=l.project_id WHERE c.project_id IS NULL"
            ).fetchone()[0]
            self.assertEqual(missing_labor_projects, 0)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
