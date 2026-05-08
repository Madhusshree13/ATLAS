"""
Apple Watch → Atlas health sync via local HTTP receiver.

Since HealthKit is iOS/macOS only, this module runs a small HTTP server
on your Windows PC. Your iPhone posts health data to it daily over Wi-Fi.

─────────────────────────────────────────────────────────────────────────────
SETUP (one-time, ~10 minutes)
─────────────────────────────────────────────────────────────────────────────
1. Find your PC's local IP:  Run `ipconfig` in cmd → look for IPv4 Address
   Example: 192.168.1.42

2. On iPhone → Shortcuts app → (+) New Shortcut:
   Name it "Atlas Health Sync"

   Add these actions:
   a) "Find Health Samples" × 5 (one per metric):
      - Steps            → today, sum
      - Heart Rate       → today, average
      - Blood Oxygen     → today, average
      - Active Energy    → today, sum
      - Body Weight      → most recent sample

   b) "Get Numbers from [each result above]" to extract the numeric value

   c) "Get contents of URL":
      URL:    http://192.168.1.42:5757/health   ← replace with your PC IP
      Method: POST
      Headers: Content-Type → application/json
      Body (JSON):
      {
        "date":             "[Current Date formatted as YYYY-MM-DD]",
        "steps":            [steps number],
        "heart_rate_avg":   [heart rate number],
        "spo2":             [blood oxygen number],
        "calories_burned":  [active energy number],
        "weight_kg":        [body weight number]
      }

3. Create an Automation:
   Shortcuts → Automation → (+) → Time of Day → 08:00 AM → Daily
   → Run Shortcut → "Atlas Health Sync" → Don't Ask Before Running

Atlas will speak a confirmation when data arrives if you are active.
─────────────────────────────────────────────────────────────────────────────
"""

import json
import socket
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer


# Fields accepted from the Apple Watch / iPhone Shortcut
_ALLOWED_FIELDS = {
    "steps", "water_ml", "sleep_start", "sleep_end", "sleep_hours",
    "meals", "workout", "workout_type", "workout_minutes",
    "heart_rate_avg", "bp_systolic", "bp_diastolic", "spo2",
    "blood_sugar", "weight_kg", "calories_burned", "mood", "notes",
}


class AppleWatchReceiver:
    """
    Background HTTP server that receives health data POSTed by an iPhone Shortcut.
    Stores records via HealthTracker.
    Calls on_sync(entry_dict) on the main thread when new data arrives.
    """

    def __init__(self, tracker, port: int = 5757, on_sync=None):
        self.tracker  = tracker
        self.port     = port
        self.on_sync  = on_sync   # optional callback(entry_dict) when data received
        self._server  = None
        self._thread  = None

    def start(self):
        tracker  = self.tracker
        on_sync  = self.on_sync

        class _Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path != "/health":
                    self.send_response(404)
                    self.end_headers()
                    return
                try:
                    length = int(self.headers.get("Content-Length", 0))
                    body   = self.rfile.read(length)
                    data   = json.loads(body)

                    record_date = data.pop("date", date.today().isoformat())
                    entry = {k: v for k, v in data.items()
                             if k in _ALLOWED_FIELDS and v is not None}
                    entry["source"] = "apple_watch"

                    tracker.log_entry(entry, for_date=record_date)
                    print(f"[Apple Watch Sync] Data received for {record_date}: {entry}")

                    if on_sync:
                        on_sync(entry)

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"OK")

                except Exception as exc:
                    print(f"[Apple Watch Sync] Error: {exc}")
                    self.send_response(400)
                    self.end_headers()

            def log_message(self, *args):
                pass  # suppress default access log noise

        self._server = HTTPServer(("0.0.0.0", self.port), _Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True
        )
        self._thread.start()

        local_ip = _get_local_ip()
        print(
            f"[Apple Watch Sync] Receiver running on {local_ip}:{self.port}\n"
            f"  → POST http://{local_ip}:{self.port}/health  (from iPhone Shortcut)\n"
            f"  → See src/health/apple_watch_sync.py for full setup instructions."
        )

    def stop(self):
        if self._server:
            self._server.shutdown()


def _get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
