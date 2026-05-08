import os
import sqlite3
from datetime import datetime


class NotesStore:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS text_notes (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    title      TEXT    DEFAULT 'Untitled',
                    content    TEXT    DEFAULT '',
                    color      TEXT    DEFAULT '#fff9c4',
                    created_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS whiteboards (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT    DEFAULT 'Untitled Board',
                    canvas_json TEXT    DEFAULT '{"objects":[]}',
                    created_at  TEXT,
                    updated_at  TEXT
                );
            """)
            conn.commit()

    # ------------------------------------------------------------------ notes

    def get_all_notes(self) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM text_notes ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def save_note(self, note_id, title: str, content: str, color: str = "#fff9c4") -> int:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            if note_id:
                conn.execute(
                    "UPDATE text_notes SET title=?, content=?, color=?, updated_at=? WHERE id=?",
                    (title, content, color, now, note_id),
                )
                return int(note_id)
            else:
                cur = conn.execute(
                    "INSERT INTO text_notes (title, content, color, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (title, content, color, now, now),
                )
                return cur.lastrowid

    def delete_note(self, note_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM text_notes WHERE id = ?", (note_id,))
            conn.commit()

    # -------------------------------------------------------------- whiteboards

    def get_all_whiteboards(self) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, updated_at FROM whiteboards ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def create_whiteboard(self, name: str = "Untitled Board") -> dict:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO whiteboards (name, canvas_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (name, '{"objects":[]}', now, now),
            )
            return {"id": cur.lastrowid, "name": name}

    def get_whiteboard_canvas(self, board_id: int) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, canvas_json FROM whiteboards WHERE id = ?", (board_id,)
            ).fetchone()
            return dict(row) if row else {}

    def save_whiteboard_canvas(self, board_id: int, canvas_json: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE whiteboards SET canvas_json = ?, updated_at = ? WHERE id = ?",
                (canvas_json, datetime.now().isoformat(), board_id),
            )
            conn.commit()

    def rename_whiteboard(self, board_id: int, name: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE whiteboards SET name = ?, updated_at = ? WHERE id = ?",
                (name, datetime.now().isoformat(), board_id),
            )
            conn.commit()

    def delete_whiteboard(self, board_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM whiteboards WHERE id = ?", (board_id,))
            conn.commit()
