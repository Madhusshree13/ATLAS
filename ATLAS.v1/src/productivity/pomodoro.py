import threading
import time


class PomodoroTimer:
    """Simple countdown timer that fires a callback on completion."""

    def __init__(self):
        self._thread     = None
        self._stop       = threading.Event()
        self._start_time = 0.0
        self._duration   = 0        # seconds
        self._on_done    = None

    # ── Control ────────────────────────────────────────────────

    def start(self, minutes: int, on_done):
        """Start a fresh timer for `minutes` minutes."""
        self.cancel()
        self._duration   = minutes * 60
        self._start_time = time.monotonic()
        self._on_done    = on_done
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        self._stop.set()
        self._duration = 0

    # ── Status ─────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def remaining_seconds(self) -> int:
        if not self.is_running:
            return 0
        elapsed = time.monotonic() - self._start_time
        return max(0, int(self._duration - elapsed))

    @property
    def total_minutes(self) -> int:
        return self._duration // 60

    # ── Internal ───────────────────────────────────────────────

    def _run(self):
        self._stop.wait(timeout=self._duration)
        if not self._stop.is_set() and self._on_done:
            self._on_done(self._duration // 60)
