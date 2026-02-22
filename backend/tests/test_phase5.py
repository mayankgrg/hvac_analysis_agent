from __future__ import annotations

import os
import sqlite3
from pathlib import Path
import unittest

from backend.db.connection import get_connection
from backend.tools.send_email import LOG_FILE, send_email
from backend.tools.what_if_margin import what_if_margin
from backend.scripts.build_dossiers import build_all

DB_PATH = Path(__file__).resolve().parents[1] / "hvac.db"


class TestPhase5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_all()

    def test_what_if_margin(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute("SELECT project_id FROM contracts LIMIT 1").fetchone()
            result = what_if_margin(conn, row[0], 100000)
            self.assertIsNotNone(result)
            self.assertIn("new_realized_margin_pct", result)
        finally:
            conn.close()

    def test_email_log_fallback(self):
        if LOG_FILE.exists():
            LOG_FILE.unlink()
        res = send_email("pm@example.com", "Test", "Body")
        self.assertEqual(res["delivery"], "logged")
        self.assertTrue(LOG_FILE.exists())


if __name__ == "__main__":
    unittest.main()
