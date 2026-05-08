import os
import sqlite3
from datetime import datetime, date


class JournalStore:
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
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_date  TEXT NOT NULL UNIQUE,
                    content     TEXT DEFAULT '',
                    mood        INTEGER,
                    created_at  TEXT,
                    updated_at  TEXT
                )
            """)

    def save(self, content: str, mood: int = None, entry_date: str = None):
        d   = entry_date or date.today().isoformat()
        now = datetime.now().isoformat()
        with self._connect() as c:
            if c.execute("SELECT id FROM journal_entries WHERE entry_date=?", (d,)).fetchone():
                c.execute(
                    "UPDATE journal_entries SET content=?, mood=?, updated_at=? WHERE entry_date=?",
                    (content, mood, now, d),
                )
            else:
                c.execute(
                    "INSERT INTO journal_entries (entry_date,content,mood,created_at,updated_at) "
                    "VALUES (?,?,?,?,?)",
                    (d, content, mood, now, now),
                )

    def get(self, entry_date: str = None) -> dict:
        d = entry_date or date.today().isoformat()
        with self._connect() as c:
            r = c.execute("SELECT * FROM journal_entries WHERE entry_date=?", (d,)).fetchone()
            return dict(r) if r else {"entry_date": d, "content": "", "mood": None}

    def recent(self, n: int = 14) -> list:
        with self._connect() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM journal_entries ORDER BY entry_date DESC LIMIT ?", (n,)
            )]

    def search(self, query: str) -> list:
        with self._connect() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM journal_entries WHERE content LIKE ? ORDER BY entry_date DESC LIMIT 20",
                (f"%{query}%",),
            )]
