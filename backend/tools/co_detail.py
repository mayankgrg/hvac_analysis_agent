from __future__ import annotations

import sqlite3


def get_co_detail(conn: sqlite3.Connection, co_number: str):
    row = conn.execute("SELECT * FROM change_orders WHERE co_number=?", (co_number,)).fetchone()
    return dict(row) if row else None
