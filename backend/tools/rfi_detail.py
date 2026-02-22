from __future__ import annotations

import sqlite3


def get_rfi_detail(conn: sqlite3.Connection, rfi_number: str):
    row = conn.execute("SELECT * FROM rfis WHERE rfi_number=?", (rfi_number,)).fetchone()
    return dict(row) if row else None
