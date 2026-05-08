import threading
import time
import psutil


# Processes to terminate when focus mode starts
_DISTRACTION_PROCS = {
    "discord.exe", "telegram.exe", "whatsapp.exe",
    "slack.exe", "messenger.exe",
}


class FocusMode:
    """Kills distraction apps on entry; optionally auto-exits after `minutes`."""

    def __init__(self):
        self._active     = False
        self._end_time   = 0.0
        self._stop       = threading.Event()
        self._thread     = None
        self._on_done    = None

    # ── Control ────────────────────────────────────────────────

    def start(self, minutes: int = None, on_done=None):
        """Enter focus mode. If `minutes` given, auto-exit after that duration."""
        if self._active:
            self.end()
        self._active  = True
        self._on_done = on_done
        self._stop.clear()
        self._kill_distractions()

        if minutes:
            self._end_time = time.monotonic() + minutes * 60
            self._thread = threading.Thread(target=self._watch, daemon=True)
            self._thread.start()

    def end(self):
        self._stop.set()
        self._active = False

    # ── Status ─────────────────────────────────────────────────

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def remaining_minutes(self) -> int:
        if not self._active or not self._end_time:
            return 0
        return max(0, int((self._end_time - time.monotonic()) / 60))

    # ── Internal ───────────────────────────────────────────────

    def _kill_distractions(self):
        killed = []
        for proc in psutil.process_iter(["name"]):
            name = (proc.info["name"] or "").lower()
            if name in _DISTRACTION_PROCS:
                try:
                    proc.terminate()
                    killed.append(name)
                except Exception:
                    pass
        if killed:
            print(f"[FocusMode] Closed: {', '.join(killed)}")

    def _watch(self):
        self._stop.wait(timeout=self._end_time - time.monotonic())
        if not self._stop.is_set():
            self._active = False
            if self._on_done:
                self._on_done()
