import os
import sqlite3
from datetime import datetime, date, timedelta


class HabitStore:
    _DEFAULTS = [
        "Exercise 💪",
        "Drink 2L Water 💧",
        "Read 30 min 📚",
        "Sleep before midnight 🌙",
        "No junk food 🥗",
    ]

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
            c.executescript("""
                CREATE TABLE IF NOT EXISTS habits (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT NOT NULL,
                    active     INTEGER DEFAULT 1,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS habit_logs (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id  INTEGER NOT NULL,
                    log_date  TEXT NOT NULL,
                    UNIQUE(habit_id, log_date)
                );
            """)
            if c.execute("SELECT COUNT(*) FROM habits").fetchone()[0] == 0:
                now = datetime.now().isoformat()
                for name in self._DEFAULTS:
                    c.execute("INSERT INTO habits (name, created_at) VALUES (?,?)", (name, now))

    # ── Habits ─────────────────────────────────────────────────

    def get_habits(self) -> list:
        with self._connect() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM habits WHERE active=1 ORDER BY id"
            )]

    def add_habit(self, name: str):
        with self._connect() as c:
            c.execute("INSERT INTO habits (name, created_at) VALUES (?,?)",
                      (name.strip(), datetime.now().isoformat()))

    def delete_habit(self, habit_id: int):
        with self._connect() as c:
            c.execute("UPDATE habits SET active=0 WHERE id=?", (habit_id,))

    # ── Logging ────────────────────────────────────────────────

    def log(self, habit_id: int, log_date: str = None):
        d = log_date or date.today().isoformat()
        with self._connect() as c:
            c.execute("INSERT OR IGNORE INTO habit_logs (habit_id, log_date) VALUES (?,?)",
                      (habit_id, d))

    def unlog(self, habit_id: int, log_date: str = None):
        d = log_date or date.today().isoformat()
        with self._connect() as c:
            c.execute("DELETE FROM habit_logs WHERE habit_id=? AND log_date=?", (habit_id, d))

    # ── Queries ────────────────────────────────────────────────

    def get_today(self) -> list:
        today = date.today().isoformat()
        habits = self.get_habits()
        with self._connect() as c:
            done = {r[0] for r in c.execute(
                "SELECT habit_id FROM habit_logs WHERE log_date=?", (today,)
            )}
        return [{"id": h["id"], "name": h["name"], "done": h["id"] in done} for h in habits]

    def get_streaks(self) -> dict:
        """Return {habit_id: streak_days}."""
        out = {}
        with self._connect() as c:
            for h in self.get_habits():
                streak, d = 0, date.today()
                while True:
                    if c.execute("SELECT 1 FROM habit_logs WHERE habit_id=? AND log_date=?",
                                 (h["id"], d.isoformat())).fetchone():
                        streak += 1
                        d -= timedelta(days=1)
                    else:
                        break
                out[h["id"]] = streak
        return out

    def get_week_history(self, days: int = 7):
        """Return ({habit_id: [bool*days]}, [date_str*days]) oldest→newest."""
        habits = self.get_habits()
        today  = date.today()
        dates  = [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]
        out    = {}
        with self._connect() as c:
            for h in habits:
                done = {r[0] for r in c.execute(
                    f"SELECT log_date FROM habit_logs WHERE habit_id=? AND log_date IN ({','.join('?'*days)})",
                    (h["id"], *dates)
                )}
                out[h["id"]] = [d in done for d in dates]
        return out, dates
