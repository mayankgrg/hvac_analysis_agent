from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import unittest

from backend.scripts.build_dossiers import build_all

DB_PATH = Path(__file__).resolve().parents[1] / "hvac.db"


class TestPhase4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_all()

    def test_portfolio_payload(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute("SELECT dossier_json FROM dossiers WHERE project_id='PORTFOLIO'").fetchone()
            self.assertIsNotNone(row)
            d = json.loads(row[0])
            self.assertEqual(d.get("project_count"), 5)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
