"""
reminder_engine.py — Background engine for health & personal reminders.

Two reminder types:
  - interval   : fires every N minutes (water, breaks)
  - scheduled  : fires once per day at HH:MM (medication, sleep)

The 30-second check loop means scheduled reminders fire within ±30 s of
the target time, which is plenty accurate for health reminders.
"""

import threading
import time
from datetime import datetime


class ReminderEngine:
    def __init__(self, speaker, signals):
        self._speaker = speaker
        self._signals = signals
        self._items   = {}        # name → config dict
        self._lock    = threading.Lock()
        threading.Thread(target=self._loop, daemon=True).start()

    # ── Public API ─────────────────────────────────────────────

    def add_interval(self, name: str, message: str, interval_minutes: int):
        """Fire `message` every `interval_minutes` minutes (first fire after one interval)."""
        with self._lock:
            self._items[name] = {
                "type":      "interval",
                "message":   message,
                "interval":  interval_minutes * 60,
                "next_fire": time.monotonic() + interval_minutes * 60,
            }
        print(f"[Reminders] +interval '{name}' every {interval_minutes} min")

    def add_scheduled(self, name: str, message: str, hour: int, minute: int = 0):
        """Fire `message` once per day at HH:MM."""
        with self._lock:
            self._items[name] = {
                "type":            "scheduled",
                "message":         message,
                "hour":            hour,
                "minute":          minute,
                "last_fired_date": None,
            }
        print(f"[Reminders] +scheduled '{name}' at {hour:02d}:{minute:02d} daily")

    def remove(self, name: str) -> bool:
        with self._lock:
            existed = name in self._items
            self._items.pop(name, None)
        if existed:
            print(f"[Reminders] removed '{name}'")
        return existed

    def clear_all(self):
        with self._lock:
            self._items.clear()
        print("[Reminders] all cleared")

    def list_all(self) -> list:
        """Return human-readable description strings for all active reminders."""
        with self._lock:
            out = []
            for name, r in self._items.items():
                if r["type"] == "interval":
                    mins = r["interval"] // 60
                    label = f"every {mins} minute{'s' if mins != 1 else ''}"
                    out.append(f"{name} ({label})")
                else:
                    out.append(f"{name} (daily at {r['hour']:02d}:{r['minute']:02d})")
            return out

    @property
    def active_names(self) -> list:
        with self._lock:
            return list(self._items.keys())

    # ── Internal ───────────────────────────────────────────────

    def _loop(self):
        while True:
            time.sleep(30)
            self._check()

    def _check(self):
        now_mono = time.monotonic()
        now_dt   = datetime.now()
        today    = now_dt.date().isoformat()

        with self._lock:
            snapshot = dict(self._items)

        for name, r in snapshot.items():
            try:
                if r["type"] == "interval":
                    if now_mono >= r["next_fire"]:
                        self._fire(r["message"])
                        with self._lock:
                            if name in self._items:
                                self._items[name]["next_fire"] = now_mono + r["interval"]

                elif r["type"] == "scheduled":
                    if (now_dt.hour   == r["hour"] and
                            now_dt.minute == r["minute"] and
                            r.get("last_fired_date") != today):
                        self._fire(r["message"])
                        with self._lock:
                            if name in self._items:
                                self._items[name]["last_fired_date"] = today

            except Exception as exc:
                print(f"[Reminders] error in '{name}': {exc}")

    def _fire(self, message: str):
        # Run in a thread so the check loop never blocks
        threading.Thread(
            target=self._speaker.speak,
            args=(message,),
            kwargs={"signals": self._signals},
            daemon=True,
        ).start()
