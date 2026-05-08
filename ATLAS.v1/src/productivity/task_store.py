import os
import sqlite3
from datetime import datetime


class TaskStore:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _init_db(self):
        with self._connect() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    title         TEXT    NOT NULL,
                    due_date      TEXT,
                    priority      TEXT    DEFAULT 'normal',
                    done          INTEGER DEFAULT 0,
                    created_at    TEXT,
                    completed_at  TEXT
                )
            """)

    # ── Write ──────────────────────────────────────────────────

    def add_task(self, title: str, due_date: str = None, priority: str = "normal") -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tasks (title, due_date, priority, done, created_at) VALUES (?,?,?,0,?)",
                (title.strip(), due_date, priority, datetime.now().isoformat()),
            )
            return cur.lastrowid

    def complete_task(self, task_id: int):
        with self._connect() as c:
            c.execute(
                "UPDATE tasks SET done=1, completed_at=? WHERE id=?",
                (datetime.now().isoformat(), task_id),
            )

    def delete_task(self, task_id: int):
        with self._connect() as c:
            c.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    # ── Fuzzy helpers (voice commands) ─────────────────────────

    def complete_by_title(self, fragment: str):
        """Complete the first pending task whose title contains fragment. Returns title or None."""
        frag = fragment.lower().strip()
        for task in self.get_pending():
            if frag in task["title"].lower():
                self.complete_task(task["id"])
                return task["title"]
        return None

    def delete_by_title(self, fragment: str):
        """Delete the first task whose title contains fragment. Returns title or None."""
        frag = fragment.lower().strip()
        for task in self.get_all():
            if frag in task["title"].lower():
                self.delete_task(task["id"])
                return task["title"]
        return None

    # ── Read ───────────────────────────────────────────────────

    def get_pending(self) -> list:
        with self._connect() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM tasks WHERE done=0 ORDER BY created_at ASC"
            )]

    def get_all(self) -> list:
        with self._connect() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM tasks ORDER BY done ASC, created_at DESC"
            )]
