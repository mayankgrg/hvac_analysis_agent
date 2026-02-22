from __future__ import annotations

import sqlite3


def get_field_notes(conn: sqlite3.Connection, project_id: str, keyword: str = "", limit: int = 20):
    keyword = f"%{keyword.lower()}%"
    return [
        dict(r)
        for r in conn.execute(
            "SELECT note_id, date, note_type, content FROM field_notes WHERE project_id=? AND LOWER(content) LIKE ? ORDER BY date DESC LIMIT ?",
            (project_id, keyword, limit),
        ).fetchall()
    ]
