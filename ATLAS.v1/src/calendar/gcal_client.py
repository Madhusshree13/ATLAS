import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    from zoneinfo import ZoneInfo
    def _tz(name):
        return ZoneInfo(name)
except ImportError:
    from datetime import timezone
    def _tz(_name):
        return timezone.utc

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarClient:
    def __init__(self, root_path):
        self.root = root_path
        self.creds_file = os.path.join(root_path, "assets", "credentials.json")
        self.token_file = os.path.join(root_path, "assets", "token.json")
        self.timezone = os.getenv("TIMEZONE", "Asia/Kolkata")
        self.service = None
        # Attempt silent auth only (no browser). Browser OAuth deferred to first use.
        self._try_silent_auth()

    def _try_silent_auth(self):
        """Load existing token and refresh if expired. Never opens a browser."""
        if not os.path.exists(self.creds_file) or not os.path.exists(self.token_file):
            return
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(self.token_file, "w") as f:
                    f.write(creds.to_json())
            if creds and creds.valid:
                self.service = build("calendar", "v3", credentials=creds)
                print("[Calendar] Connected (token loaded).")
        except Exception as e:
            print(f"[Calendar] Silent auth failed: {e}")

    def _ensure_service(self) -> bool:
        """Connect if not already connected. Runs browser OAuth on first use."""
        if self.service:
            return True
        if not os.path.exists(self.creds_file):
            print("[Calendar] credentials.json not found — cannot authenticate.")
            return False
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds = None
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    print("[Calendar] Opening browser for one-time Google sign-in...")
                    flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(self.token_file, "w") as f:
                    f.write(creds.to_json())

            self.service = build("calendar", "v3", credentials=creds)
            print("[Calendar] Connected.")
            return True
        except Exception as e:
            print(f"[Calendar] Auth error: {e}")
            return False

    def create_event(self, title, start_dt, description="", duration_minutes=30, reminder_minutes=15):
        if not self._ensure_service():
            return None
        try:
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            event = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start_dt.isoformat(), "timeZone": self.timezone},
                "end": {"dateTime": end_dt.isoformat(), "timeZone": self.timezone},
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": reminder_minutes},
                        {"method": "email", "minutes": reminder_minutes},
                    ],
                },
            }
            created = self.service.events().insert(calendarId="primary", body=event).execute()
            return created.get("htmlLink", "")
        except Exception as e:
            print(f"[Calendar] create event error: {e}")
            return None

    def get_today_events(self):
        """Return all calendar events for today, sorted by start time."""
        tz = _tz(self.timezone)
        today = datetime.now(tz).date()
        start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=tz)
        end_of_day   = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=tz)
        return self.get_events_in_range(start_of_day, end_of_day)

    def get_events_in_range(self, start_dt, end_dt):
        """Return list of calendar events that fall within [start_dt, end_dt]."""
        if not self._ensure_service():
            return []
        try:
            result = self.service.events().list(
                calendarId="primary",
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            events = []
            for item in result.get("items", []):
                events.append({
                    "id":    item.get("id"),
                    "title": item.get("summary", "Busy"),
                    "start": item["start"].get("dateTime") or item["start"].get("date"),
                    "end":   item["end"].get("dateTime")   or item["end"].get("date"),
                })
            return events
        except Exception as e:
            print(f"[Calendar] get_events_in_range error: {e}")
            return []

    def check_conflicts(self, start_dt, end_dt):
        """Return any events that overlap with the proposed [start_dt, end_dt] window."""
        return self.get_events_in_range(start_dt, end_dt)

    def find_next_free_slot(self, preferred_dt, duration_minutes, work_start=9, work_end=18, max_days=7):
        """
        Starting from preferred_dt, walk forward in time (within working hours) until
        a gap of at least duration_minutes is found with no calendar conflicts.
        Returns the start datetime of that gap, or None if none found within max_days.
        """
        tz = _tz(self.timezone)
        slot = preferred_dt

        for _ in range(max_days * 96):  # up to 15-min increments per day
            local = slot.astimezone(tz)

            if local.hour < work_start:
                slot = local.replace(hour=work_start, minute=0, second=0, microsecond=0)
                local = slot
            elif local.hour >= work_end:
                next_day = (local + timedelta(days=1)).replace(
                    hour=work_start, minute=0, second=0, microsecond=0)
                slot = next_day
                local = slot

            slot_end = slot + timedelta(minutes=duration_minutes)
            local_end = slot_end.astimezone(tz)

            if local_end.hour > work_end or (local_end.hour == work_end and local_end.minute > 0):
                next_day = (local + timedelta(days=1)).replace(
                    hour=work_start, minute=0, second=0, microsecond=0)
                slot = next_day
                continue

            conflicts = self.get_events_in_range(slot, slot_end)
            if not conflicts:
                return slot

            latest_end = slot
            for ev in conflicts:
                try:
                    ev_end = datetime.fromisoformat(ev["end"])
                    if ev_end.tzinfo is None:
                        ev_end = ev_end.replace(tzinfo=tz)
                    if ev_end > latest_end:
                        latest_end = ev_end
                except Exception:
                    pass
            slot = latest_end + timedelta(minutes=5)

        return None
