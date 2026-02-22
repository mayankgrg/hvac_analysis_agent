from __future__ import annotations

import csv
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "hvac.db"
SCHEMA = ROOT / "db" / "schema.sql"

TABLE_FILES = {
    "contracts": "contracts.csv",
    "sov": "sov.csv",
    "sov_budget": "sov_budget.csv",
    "labor_logs": "labor_logs.csv",
    "material_deliveries": "material_deliveries.csv",
    "billing_history": "billing_history.csv",
    "billing_line_items": "billing_line_items.csv",
    "change_orders": "change_orders.csv",
    "rfis": "rfis.csv",
    "field_notes": "field_notes.csv",
}


def seed_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        with SCHEMA.open("r", encoding="utf-8") as f:
            conn.executescript(f.read())

        for table, filename in TABLE_FILES.items():
            path = DATA_DIR / filename
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                cols = reader.fieldnames or []
                placeholders = ",".join(["?"] * len(cols))
                col_names = ",".join(cols)
                sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                rows = [tuple(row.get(c, None) for c in cols) for row in reader]
                conn.executemany(sql, rows)

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    seed_db()
    print(f"Seeded DB at {DB_PATH}")
