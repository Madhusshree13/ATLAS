import os
import sqlite3
from datetime import datetime, date, timedelta
from statistics import mean


_COLUMNS = [
    "record_date", "steps", "water_ml", "sleep_start", "sleep_end",
    "sleep_hours", "meals", "workout", "workout_type", "workout_minutes",
    "heart_rate_avg", "bp_systolic", "bp_diastolic", "spo2", "blood_sugar",
    "weight_kg", "calories_burned", "mood", "notes", "source",
    "created_at", "updated_at",
]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS health_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date     TEXT NOT NULL UNIQUE,
    steps           INTEGER,
    water_ml        INTEGER,
    sleep_start     TEXT,
    sleep_end       TEXT,
    sleep_hours     REAL,
    meals           INTEGER,
    workout         INTEGER DEFAULT 0,
    workout_type    TEXT,
    workout_minutes INTEGER,
    heart_rate_avg  INTEGER,
    bp_systolic     INTEGER,
    bp_diastolic    INTEGER,
    spo2            INTEGER,
    blood_sugar     REAL,
    weight_kg       REAL,
    calories_burned INTEGER,
    mood            INTEGER,
    notes           TEXT,
    source          TEXT DEFAULT 'manual',
    created_at      TEXT,
    updated_at      TEXT
)
"""


class HealthTracker:
    RETENTION_DAYS = 90

    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(_SCHEMA)
            conn.commit()

    def _prune(self):
        cutoff = (date.today() - timedelta(days=self.RETENTION_DAYS)).isoformat()
        with self._connect() as conn:
            conn.execute("DELETE FROM health_records WHERE record_date < ?", (cutoff,))
            conn.commit()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def log_entry(self, entry: dict, for_date: str = None):
        """
        Upsert a health record for a given date.
        entry: dict with any subset of the health fields.
        Existing fields are preserved; only provided fields are overwritten.
        """
        record_date = for_date or date.today().isoformat()
        now = datetime.now().isoformat()

        if entry.get("sleep_start") and entry.get("sleep_end"):
            entry["sleep_hours"] = _compute_sleep_hours(
                entry["sleep_start"], entry["sleep_end"]
            )

        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM health_records WHERE record_date = ?", (record_date,)
            ).fetchone()

            if existing:
                updates = {k: v for k, v in entry.items()
                           if v is not None and k in _COLUMNS and k != "record_date"}
                updates["updated_at"] = now
                clause = ", ".join(f"{k} = ?" for k in updates)
                conn.execute(
                    f"UPDATE health_records SET {clause} WHERE record_date = ?",
                    [*updates.values(), record_date],
                )
            else:
                fields = {
                    "record_date": record_date,
                    "created_at":  now,
                    "updated_at":  now,
                }
                fields.update(
                    {k: v for k, v in entry.items()
                     if k in _COLUMNS and v is not None}
                )
                cols = list(fields.keys())
                conn.execute(
                    f"INSERT INTO health_records ({', '.join(cols)}) "
                    f"VALUES ({', '.join('?' * len(cols))})",
                    list(fields.values()),
                )
            conn.commit()

        self._prune()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_entry(self, for_date: str = None) -> dict:
        record_date = for_date or date.today().isoformat()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM health_records WHERE record_date = ?", (record_date,)
            ).fetchone()
            return dict(row) if row else {}

    def get_range(self, days: int = 30) -> list:
        since = (date.today() - timedelta(days=days - 1)).isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM health_records WHERE record_date >= ? "
                "ORDER BY record_date DESC",
                (since,),
            ).fetchall()
            return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def compute_analytics(self, days: int = 7) -> dict:
        records = self.get_range(days)
        if not records:
            return {}

        def avg_f(field):
            vals = [r[field] for r in records if r.get(field) is not None]
            return round(mean(vals), 1) if vals else None

        def trend(field):
            pts = sorted(
                [(r["record_date"], r[field]) for r in records
                 if r.get(field) is not None],
                key=lambda x: x[0],
            )
            if len(pts) < 3:
                return None
            half = len(pts) // 2
            first  = mean(v for _, v in pts[:half])
            second = mean(v for _, v in pts[half:])
            diff = second - first
            if abs(diff) < 0.05 * (abs(first) or 1):
                return "stable"
            return "improving" if diff > 0 else "declining"

        workout_days = sum(1 for r in records if r.get("workout"))
        result = {
            "period_days":        len(records),
            "avg_steps":          avg_f("steps"),
            "avg_water_ml":       avg_f("water_ml"),
            "avg_sleep_hours":    avg_f("sleep_hours"),
            "avg_heart_rate":     avg_f("heart_rate_avg"),
            "avg_spo2":           avg_f("spo2"),
            "avg_blood_sugar":    avg_f("blood_sugar"),
            "avg_weight_kg":      avg_f("weight_kg"),
            "workout_days":       workout_days,
            "workout_frequency":  f"{workout_days} of {len(records)} days",
            "steps_trend":        trend("steps"),
            "sleep_trend":        trend("sleep_hours"),
            "water_trend":        trend("water_ml"),
        }
        return {k: v for k, v in result.items() if v is not None}

    def find_patterns(self, days: int = 30) -> list:
        records = self.get_range(days)
        n = len(records)
        if n < 5:
            return []

        patterns = []

        # "late" = bedtime between 1 AM and 5 AM (cross-midnight, not just 11 PM)
        late = [r for r in records if r.get("sleep_start") and 1 <= _hour(r["sleep_start"]) <= 5]
        if len(late) >= n * 0.4:
            patterns.append(
                f"You frequently sleep after 1 AM ({len(late)} of {n} tracked days)."
            )

        short = [r for r in records if r.get("sleep_hours") and r["sleep_hours"] < 7]
        if len(short) >= n * 0.4:
            avg_s = round(mean(r["sleep_hours"] for r in short), 1)
            patterns.append(
                f"Your sleep averages {avg_s} hours on low-sleep nights — below the recommended 7–9."
            )

        low_water = [r for r in records if r.get("water_ml") and r["water_ml"] < 2000]
        if len(low_water) >= n * 0.3:
            patterns.append("Hydration is consistently below 2 litres on many tracked days.")

        low_steps = [r for r in records if r.get("steps") and r["steps"] < 7000]
        if len(low_steps) >= n * 0.4:
            patterns.append(
                "Step count falls below 7,000 on most days — consider adding short walks."
            )

        workout_days = sum(1 for r in records if r.get("workout"))
        freq = workout_days / n
        if freq == 0:
            patterns.append(
                "No workouts logged yet. Even 20 minutes of movement a day makes a difference."
            )
        elif freq < 0.3:
            patterns.append(
                f"You work out on about {int(freq * 100)}% of days — "
                "aim for at least 3–4 sessions per week."
            )

        spo2_vals = [r["spo2"] for r in records if r.get("spo2")]
        if spo2_vals and mean(spo2_vals) < 95:
            patterns.append(
                f"Average SpO2 is {round(mean(spo2_vals), 1)}% — "
                "consistently below 95% warrants medical attention."
            )

        return patterns

    # ------------------------------------------------------------------
    # Formatted summary (for TTS / LLM context)
    # ------------------------------------------------------------------

    def format_entry(self, entry: dict) -> str:
        lines = []
        if entry.get("steps"):          lines.append(f"Steps: {entry['steps']:,}")
        if entry.get("water_ml"):       lines.append(f"Water: {entry['water_ml'] / 1000:.1f} L")
        if entry.get("sleep_hours"):
            st = entry.get("sleep_start", "?")
            en = entry.get("sleep_end", "?")
            lines.append(f"Sleep: {entry['sleep_hours']} h ({st} – {en})")
        if entry.get("meals"):          lines.append(f"Meals: {entry['meals']}")
        if entry.get("workout"):
            wt = entry.get("workout_type") or "general"
            wm = entry.get("workout_minutes")
            lines.append(f"Workout: {wt}" + (f" ({wm} min)" if wm else ""))
        if entry.get("heart_rate_avg"): lines.append(f"Heart rate: {entry['heart_rate_avg']} bpm")
        if entry.get("spo2"):           lines.append(f"SpO2: {entry['spo2']}%")
        if entry.get("bp_systolic"):
            lines.append(f"BP: {entry['bp_systolic']}/{entry.get('bp_diastolic', '?')} mmHg")
        if entry.get("blood_sugar"):    lines.append(f"Blood sugar: {entry['blood_sugar']} mg/dL")
        if entry.get("weight_kg"):      lines.append(f"Weight: {entry['weight_kg']} kg")
        if entry.get("calories_burned"):lines.append(f"Calories burned: {entry['calories_burned']}")
        return "\n".join(lines) if lines else "No data recorded yet."


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _compute_sleep_hours(start: str, end: str) -> float:
    fmt = "%H:%M"
    try:
        s = datetime.strptime(start, fmt)
        e = datetime.strptime(end, fmt)
        if e <= s:
            e += timedelta(days=1)
        return round((e - s).seconds / 3600, 2)
    except Exception:
        return None


def _hour(time_str: str) -> int:
    try:
        return int(time_str.split(":")[0])
    except Exception:
        return 0
