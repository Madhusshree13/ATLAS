"""import sys
import os
import time
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, QObject
from src.gui.overlay import AtlasAvatar
from src.voice.listener import AtlasListener
from src.voice.speaker import AtlasSpeaker

# 1. This "Messenger" handles the jump from the background thread to the UI
class AtlasSignals(QObject):
    toggle_avatar = pyqtSignal(bool)

def voice_worker(signals, speaker):
    # The Ear: Runs in the background so the GUI doesn't freeze.
    listener = AtlasListener()
    is_active = False
    
    print("--- Atlas Systems Online ---")

    while True:
        # We removed the 'Atlas is listening' print from here to prevent terminal lag
        word = listener.listen_for_wake_word()
        
        if word == "alexa":
            if not is_active:
                print(">> Waking Up...")
                signals.toggle_avatar.emit(True) # Tell UI to show
                is_active = True
                speaker.speak("I am here.")
            else:
                print(">> Going to Sleep...")
                speaker.speak("Goodbye.")
                signals.toggle_avatar.emit(False) # Tell UI to hide
                is_active = False
            
            # Flush and cooldown
            listener.model.reset()
            time.sleep(1.5)
        
        # Tiny sleep to save Ryzen CPU cycles
        time.sleep(0.01)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Path logic
    root = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(root, "assets", "avatars", "default", "atlas_transparent.png")
    
    # 1. Initialize Components
    avatar = AtlasAvatar(img_path)
    avatar.hide_atlas()
    speaker = AtlasSpeaker()
    
    # 2. Setup Signals
    signals = AtlasSignals()
    signals.toggle_avatar.connect(lambda show: avatar.show_atlas() if show else avatar.hide_atlas())
    
    # 3. Start Voice Thread
    threading.Thread(target=voice_worker, args=(signals, speaker), daemon=True).start()
    
    sys.exit(app.exec())"""
    
# import sys
# import os
# import threading
# import time
# import speech_recognition as sr
# from PyQt6.QtWidgets import QApplication
# from PyQt6.QtCore import pyqtSignal, QObject
# from src.gui.overlay import AtlasAvatar
# from src.voice.listener import AtlasListener
# from src.voice.speaker import AtlasSpeaker
# from src.brain.llm_client import AtlasBrain

# class AtlasSignals(QObject):
#     toggle_avatar = pyqtSignal(bool)

# def voice_worker(signals, speaker, brain):
#     wake_listener = AtlasListener()
#     stt_recorder = sr.Recognizer() 
#     is_active = False

#     print("--- Atlas Online: Waiting for 'Alexa' ---")

#     while True:
#         # 1. Always check for Wake Word
#         word = wake_listener.listen_for_wake_word()
        
#         if word == "alexa":
#             if not is_active:
#                 print(">> Waking Up...")
#                 signals.toggle_avatar.emit(True)
#                 is_active = True
#                 speaker.speak("I'm awake. How can I help?")
#                 wake_listener.model.reset()
#             else:
#                 print(">> Going to Sleep...")
#                 speaker.speak("Goodbye.")
#                 signals.toggle_avatar.emit(False)
#                 is_active = False
#                 wake_listener.model.reset()
#                 time.sleep(2) 
#                 continue

#         # 2. Conversation Logic (Only if visible)
#         if is_active:
#             try:
#                 with sr.Microphone() as source:
#                     # Shorten noise adjustment to keep Atlas responsive
#                     stt_recorder.adjust_for_ambient_noise(source, duration=0.5)
#                     print("Listening...")
                    
#                     # Listen for user speech
#                     audio = stt_recorder.listen(source, timeout=5, phrase_time_limit=8)
                    
#                     # TRY TO RECOGNIZE (This is where the crash happened)
#                     try:
#                         user_text = stt_recorder.recognize_google(audio)
#                         print(f"You: {user_text}")
                        
#                         # Think and Speak
#                         ai_response = brain.think(user_text)
#                         print(f"Atlas: {ai_response}")
                        
#                         # Blocking speaker prevents the 'Alexa' loop
#                         speaker.speak(ai_response)
                        
#                         # Reset wake-word buffer after Atlas talks
#                         wake_listener.model.reset()
                        
#                     except sr.RequestError as e:
#                         print(f"Network Error: Check your internet. ({e})")
#                     except sr.UnknownValueError:
#                         # This triggers if it hears noise but no words
#                         pass
                        
#             except (sr.WaitTimeoutError, Exception) as e:
#                 # Catching timeout or mic-busy errors to keep thread alive
#                 pass

#         time.sleep(0.01)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     root = r"C:\Users\madhu\OneDrive\Desktop\Atlas"
#     img_path = os.path.join(root, "assets", "avatars", "default", "atlas_transparent.png")
    
#     avatar = AtlasAvatar(img_path)
#     avatar.hide_atlas()
#     speaker = AtlasSpeaker()
#     brain = AtlasBrain()
    
#     signals = AtlasSignals()
#     signals.toggle_avatar.connect(lambda show: avatar.show_atlas() if show else avatar.hide_atlas())
    
#     threading.Thread(target=voice_worker, args=(signals, speaker, brain), daemon=True).start()
    
#     sys.exit(app.exec())



# import sys
# import os
# import threading
# import time
# import speech_recognition as sr
# from PyQt6.QtWidgets import QApplication
# from PyQt6.QtCore import pyqtSignal, QObject

# # Importing your custom modules
# from src.gui.overlay import AtlasAvatar
# from src.voice.listener import AtlasListener
# from src.voice.speaker import AtlasSpeaker
# from src.brain.llm_client import AtlasBrain
# from pynput import keyboard
# from src.gui.settings import AtlasControlPanel




# class AtlasSignals(QObject):
#     """Handles communication between background threads and the UI."""
#     toggle_avatar = pyqtSignal(bool)
#     update_avatar = pyqtSignal(str) # For mouth/hand animations

# def voice_worker(signals, speaker, brain):
#     """The main logic loop running in the background."""
#     wake_listener = AtlasListener()
#     stt_recorder = sr.Recognizer() 
#     is_active = False

#     print("--- Atlas Online: Ready for Interaction ---")

#     while True:
#         # 1. Listen for Wake Word ("Alexa")
#         word = wake_listener.listen_for_wake_word()
        
#         if word == "alexa":
#             if not is_active:
#                 print(">> Waking Up...")
#                 signals.toggle_avatar.emit(True)
#                 is_active = True
#                 # Pass 'signals' so the speaker can animate the mouth
#                 speaker.speak("I am here. How can I help you today?", signals=signals)
#                 wake_listener.model.reset()
#             else:
#                 print(">> Going to Sleep...")
#                 speaker.speak("Goodbye for now.", signals=signals)
#                 signals.toggle_avatar.emit(False)
#                 is_active = False
#                 wake_listener.model.reset()
#                 time.sleep(2) # Prevent accidental re-trigger from echo
#                 continue

#         # 2. Conversation Logic (Only if Atlas is visible)
#         if is_active:
#             try:
#                 with sr.Microphone() as source:
#                     # Speed up response by reducing silence detection time
#                     stt_recorder.pause_threshold = 0.6 
#                     stt_recorder.adjust_for_ambient_noise(source, duration=0.5)
                    
#                     print("Listening...")
#                     audio = stt_recorder.listen(source, timeout=5, phrase_time_limit=8)
                    
#                     try:
#                         # Convert speech to text via Google
#                         user_text = stt_recorder.recognize_google(audio)
#                         print(f"You: {user_text}")
                        
#                         # Generate AI response via Groq
#                         ai_response = brain.think(user_text)
#                         print(f"Atlas: {ai_response}")
                        
#                         # Speak with Animation
#                         speaker.speak(ai_response, signals=signals)
                        
#                         # Clear wake-word memory so she doesn't hear 'Alexa' in her own voice
#                         wake_listener.model.reset()
                        
#                     except sr.RequestError:
#                         print("Network Error: Check your connection.")
#                     except sr.UnknownValueError:
#                         # Triggered if background noise is heard but no words
#                         pass
                        
#             except (sr.WaitTimeoutError, Exception):
#                 # Keeps the thread alive if the mic times out
#                 pass

#         time.sleep(0.01)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     # Path Setup (Adjust to your local folder)
#     root_folder = r"C:\\Users\\madhu\\OneDrive\\Desktop\\Atlas"
    
#     # 1. Initialize UI (Animated Avatar)
#     avatar = AtlasAvatar(root_folder)
#     avatar.hide_atlas()
    
#     # 2. Initialize Speaker & Brain
#     speaker = AtlasSpeaker()
#     brain = AtlasBrain()
    
#     # 3. Connect Signals
#     signals = AtlasSignals()
    
#     # Connect Visibility Signal
#     signals.toggle_avatar.connect(lambda show: avatar.show_atlas() if show else avatar.hide_atlas())
    
#     # Connect Animation Signal (Mouth/Gestures)
#     signals.update_avatar.connect(avatar.update_frame)
    
#     # 4. Start the Logic Thread
#     logic_thread = threading.Thread(
#         target=voice_worker, 
#         args=(signals, speaker, brain), 
#         daemon=True
#     )
#     logic_thread.start()
    
#     # Run the App
#     try:
#         sys.exit(app.exec())
#     except KeyboardInterrupt:
#         print("Shutting down Atlas...")
#         sys.exit(0)



import sys
import os
import re
import socket
import threading
import time
import speech_recognition as sr
import dateparser
from datetime import datetime, timedelta

# Force UTF-8 console output on Windows so emoji / arrow characters don't crash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── Single-instance lock ──────────────────────────────────────────────────────
_LOCK_PORT = 59483  # arbitrary local port used as a process lock

def _acquire_instance_lock():
    """Bind a local socket as a single-instance lock.
    Returns the socket (must stay referenced to keep the port bound).
    Exits immediately if another Atlas instance already holds the lock.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    try:
        sock.bind(("127.0.0.1", _LOCK_PORT))
        return sock
    except OSError:
        print("Atlas is already running — only one instance allowed.")
        print("Close the existing Atlas window and try again.")
        sys.exit(1)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, QObject
from pynput import keyboard

from src.gui.overlay import AtlasAvatar
from src.gui.settings import AtlasControlPanel
from src.voice.listener import AtlasListener
from src.voice.speaker import AtlasSpeaker, AtlasInterrupted
from src.brain.llm_client import AtlasBrain
from src.brain.intent_router import IntentRouter
from src.email.gmail_client import GmailClient
from src.calendar.gcal_client import GoogleCalendarClient
from src.apps.app_launcher import AppLauncher
from src.health.health_tracker import HealthTracker
from src.health.apple_watch_sync import AppleWatchReceiver
from src.dashboard.server import start_server as start_dashboard, send_command as dashboard_cmd, clear_section as clear_dashboard_cache
from src.dashboard.notes_store    import NotesStore
from src.dashboard.habit_store    import HabitStore
from src.dashboard.finance_store  import FinanceStore
from src.dashboard.journal_store  import JournalStore
from src.productivity.task_store import TaskStore
from src.productivity.pomodoro import PomodoroTimer
from src.productivity.focus_mode      import FocusMode
from src.productivity.reminder_engine import ReminderEngine
from src.info.tools import get_weather, define_word
from src.system.media_control import (
    play_pause, next_track, prev_track, mute as media_mute,
    volume_up, volume_down, set_volume_percent,
)
from src.integrations.drive_client import DriveClient
from src.integrations.whatsapp_client import WhatsAppClient
from src.integrations.github_client import GitHubClient
from src.integrations.notion_client import NotionClient
from src.integrations.spotify_client import SpotifyClient
import ctypes
import subprocess


# ── Clipboard helpers (Windows ctypes — no extra packages) ──
_CF_UNICODE = 13

def _get_clipboard() -> str:
    try:
        if not ctypes.windll.user32.OpenClipboard(None):
            return ""
        try:
            h = ctypes.windll.user32.GetClipboardData(_CF_UNICODE)
            if not h:
                return ""
            p = ctypes.windll.kernel32.GlobalLock(h)
            text = ctypes.wstring_at(p) if p else ""
            ctypes.windll.kernel32.GlobalUnlock(h)
            return text.strip()
        finally:
            ctypes.windll.user32.CloseClipboard()
    except Exception:
        return ""

def _set_clipboard(text: str):
    try:
        buf = (text + "\0").encode("utf-16-le")
        h = ctypes.windll.kernel32.GlobalAlloc(0x0002, len(buf))
        if not h:
            return
        p = ctypes.windll.kernel32.GlobalLock(h)
        ctypes.memmove(p, buf, len(buf))
        ctypes.windll.kernel32.GlobalUnlock(h)
        if ctypes.windll.user32.OpenClipboard(None):
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.SetClipboardData(_CF_UNICODE, h)
            ctypes.windll.user32.CloseClipboard()
    except Exception:
        pass


class AtlasSignals(QObject):
    toggle_avatar = pyqtSignal(bool)
    update_avatar = pyqtSignal(str)
    show_settings = pyqtSignal()


# ---------------------------------------------------------------------------
# Speech helpers
# ---------------------------------------------------------------------------

def listen_for_speech(stt, timeout=8, phrase_time_limit=15):
    """Blocking listen: returns transcribed text or None on silence/timeout.

    timeout          — seconds to wait for speech to START (default 8)
    phrase_time_limit — max seconds of continuous speech captured (default 15)
    """
    try:
        with sr.Microphone() as source:
            audio = stt.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return stt.recognize_google(audio)
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return None
    except sr.RequestError:
        print("Network Error: Check Connection.")
        return None
    except Exception:
        return None


def listen_for_confirmation(stt, timeout=12, phrase_time_limit=8):
    """Like listen_for_speech but recalibrates the energy threshold first.

    Use this immediately after a long TTS response.  dynamic_energy_threshold
    can push the threshold up while the speakers are playing; this resets it
    to actual room-noise level so the user's 'yes'/'no' is reliably heard.
    """
    time.sleep(0.25)  # let room echo from TTS fade
    try:
        with sr.Microphone() as source:
            stt.adjust_for_ambient_noise(source, duration=0.4)
    except Exception:
        pass
    return listen_for_speech(stt, timeout=timeout, phrase_time_limit=phrase_time_limit)


# ---------------------------------------------------------------------------
# Passive dashboard-close listener (no wake word required)
# ---------------------------------------------------------------------------

_CLOSE_PHRASES = frozenset({
    "close dashboard", "close the dashboard", "shut the dashboard",
    "hide dashboard", "close my dashboard",
})


def _make_passive_listener(speaker, signals):
    """Background STT that closes the dashboard when heard, without a wake word."""
    _stop_ref = [None]

    def _cb(recognizer, audio):
        try:
            text = recognizer.recognize_google(audio).lower().strip()
            if any(p in text for p in _CLOSE_PHRASES):
                print(f"[Passive] '{text}' → closing dashboard")
                dashboard_cmd("close")
                speaker.speak("Dashboard closed.", signals=signals)
                if _stop_ref[0]:
                    _stop_ref[0](wait_for_stop=False)
                    _stop_ref[0] = None
        except (sr.UnknownValueError, sr.RequestError):
            pass
        except Exception as e:
            print(f"[Passive listener] {e}")

    def start():
        if _stop_ref[0]:
            return
        try:
            r = sr.Recognizer()
            r.pause_threshold = 0.5
            mic = sr.Microphone()
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
            _stop_ref[0] = r.listen_in_background(mic, _cb, phrase_time_limit=5)
            print("[Passive listener] Active — say 'close dashboard' anytime")
        except Exception as e:
            print(f"[Passive listener] Failed to start: {e}")

    def stop():
        if _stop_ref[0]:
            _stop_ref[0](wait_for_stop=False)
            _stop_ref[0] = None

    return start, stop


# ---------------------------------------------------------------------------
# Task handlers
# ---------------------------------------------------------------------------

_DURATION_MAP = [
    # (keyword, minutes) — checked in order; first match wins
    ("quick chat",  15), ("quick call",  15), ("standup",  15),
    ("stand-up",    15), ("stand up",    15), ("scrum",    15),
    ("huddle",      15), ("check-in",    15), ("check in", 15),
    ("1:1",         45), ("1 on 1",      45), ("one on one", 45),
    ("coffee",      45), ("review",      45), ("demo",     45),
    ("callback",    30), ("call back",   30), ("follow-up", 30),
    ("follow up",   30), ("phone",       30), ("call",     30),
    ("lunch",       60), ("dinner",      60), ("catch up", 60),
    ("sync",        60), ("discussion",  60), ("meeting",  60),
    ("interview",   60), ("presentation", 60),
    ("webinar",     90),
    ("workshop",   120), ("training",   120), ("seminar",  120),
]


def infer_duration(event_title, duration_str=None):
    """Return meeting duration in minutes from explicit phrase or event title keywords."""
    if duration_str:
        s = duration_str.lower()
        m = re.search(r'(\d+\.?\d*)\s*hour', s)
        if m:
            return max(15, int(float(m.group(1)) * 60))
        m = re.search(r'(\d+)\s*min', s)
        if m:
            return max(15, int(m.group(1)))
        if "an hour" in s or "one hour" in s:
            return 60
        if "half" in s and "hour" in s:
            return 30

    if event_title:
        title_lower = event_title.lower()
        for keyword, minutes in _DURATION_MAP:
            if keyword in title_lower:
                return minutes
    return 30  # sensible default


def _fmt_time(dt):
    """Format a datetime as readable speech string."""
    return dt.strftime("%A, %B %d at %I:%M %p").replace(" 0", " ").replace("AM", "a.m.").replace("PM", "p.m.")


def _fmt_duration(minutes):
    if minutes < 60:
        return f"{minutes} minutes"
    hours = minutes // 60
    rem = minutes % 60
    label = f"{hours} hour{'s' if hours > 1 else ''}"
    return f"{label} {rem} minutes" if rem else label


def handle_schedule(ctx, entities, ref_email=None):
    """Schedule a calendar event with collision detection and smart duration inference."""
    stt      = ctx["stt"]
    signals  = ctx["signals"]
    speaker  = ctx["speaker"]
    gcal     = ctx["gcal"]

    datetime_str = entities.get("datetime_str", "")
    duration_str = entities.get("duration_str", "")
    person       = entities.get("person_name")

    if not person and ref_email:
        match = re.search(r'[\w\.\+\-]+@[\w\.\-]+', ref_email.get("sender", ""))
        person = match.group(0) if match else ref_email.get("sender", "contact")
    person = person or "contact"

    if not datetime_str:
        speaker.speak("When should I schedule this?", signals=signals)
        response = listen_for_speech(stt)
        if response:
            datetime_str = response
        else:
            speaker.speak("Couldn't catch the time. Scheduling cancelled.", signals=signals)
            return

    tz = os.getenv("TIMEZONE", "Asia/Kolkata")
    dp_settings = {"TIMEZONE": tz, "RETURN_AS_TIMEZONE_AWARE": True, "PREFER_DATES_FROM": "future"}

    event_dt = dateparser.parse(datetime_str, settings=dp_settings)
    if not event_dt:
        speaker.speak("I couldn't parse that time. Please try again with a clearer date and time.", signals=signals)
        return

    title    = entities.get("event_title") or f"Meeting with {person}"
    duration = infer_duration(title, duration_str)

    work_start = int(os.getenv("WORK_START_HOUR", 9))
    work_end   = int(os.getenv("WORK_END_HOUR", 18))

    # --- Conflict check ---
    slot_end  = event_dt + timedelta(minutes=duration)
    conflicts = gcal.check_conflicts(event_dt, slot_end)

    if conflicts:
        conflict_name = conflicts[0]["title"]
        try:
            conflict_start_dt = datetime.fromisoformat(conflicts[0]["start"])
            conflict_time = conflict_start_dt.strftime("%I:%M %p").lstrip("0")
        except Exception:
            conflict_time = "that time"

        speaker.speak(
            f"You already have '{conflict_name}' at {conflict_time}. "
            "Let me find the next available slot.",
            signals=signals,
        )

        next_slot = gcal.find_next_free_slot(event_dt, duration, work_start, work_end)

        if next_slot:
            speaker.speak(
                f"The next free slot is {_fmt_time(next_slot)} "
                f"for {_fmt_duration(duration)}. Shall I book it?",
                signals=signals,
            )
            confirm = listen_for_speech(stt)
            if confirm and any(w in confirm.lower() for w in
                               ["yes", "sure", "okay", "ok", "go ahead", "do it", "schedule", "book"]):
                event_dt = next_slot
            else:
                speaker.speak("Alright. What time would you prefer?", signals=signals)
                new_time = listen_for_speech(stt)
                if not new_time:
                    speaker.speak("Scheduling cancelled.", signals=signals)
                    return
                new_dt = dateparser.parse(new_time, settings=dp_settings)
                if not new_dt:
                    speaker.speak("Couldn't parse that time. Scheduling cancelled.", signals=signals)
                    return
                new_conflicts = gcal.check_conflicts(new_dt, new_dt + timedelta(minutes=duration))
                if new_conflicts:
                    speaker.speak(
                        f"That time also conflicts with '{new_conflicts[0]['title']}'. "
                        "Scheduling cancelled — please try again.",
                        signals=signals,
                    )
                    return
                event_dt = new_dt
        else:
            speaker.speak(
                "I couldn't find a free slot in the next week during working hours. "
                "Please specify a time manually.",
                signals=signals,
            )
            return

    # --- Create the event ---
    speaker.speak(
        f"Scheduling '{title}' on {_fmt_time(event_dt)} for {_fmt_duration(duration)}. One moment.",
        signals=signals,
    )
    link = gcal.create_event(title, event_dt, duration_minutes=duration, reminder_minutes=15)

    if link:
        speaker.speak(
            f"Done. '{title}' is confirmed on your calendar for {_fmt_duration(duration)}. "
            "You'll be reminded 15 minutes before.",
            signals=signals,
        )
    else:
        speaker.speak("Event created. Note: calendar sync may need setup — check the console.", signals=signals)

    # Push live update to the dashboard
    clear_dashboard_cache("meetings")
    dashboard_cmd("refresh:meetings")


def _load_email_contacts(root_folder: str) -> dict:
    """Load name → email mapping from data/email_contacts.json."""
    import json
    path = os.path.join(root_folder, "data", "email_contacts.json")
    try:
        if os.path.exists(path):
            with open(path) as f:
                return {k.lower(): v for k, v in json.load(f).items()}
    except Exception:
        pass
    return {}


def _resolve_email(name: str, root_folder: str) -> str:
    """Return email address for a contact name, or None if not found."""
    contacts = _load_email_contacts(root_folder)
    name_lower = name.lower().strip()
    if name_lower in contacts:
        return contacts[name_lower]
    for k, v in contacts.items():
        if name_lower in k or k in name_lower:
            return v
    # If it looks like a raw email address already, use it directly
    if "@" in name:
        return name
    return None


def handle_send_email(ctx, entities, user_text):
    """Compose and send a new email to a named contact or email address."""
    stt     = ctx["stt"]
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    brain   = ctx["brain"]
    gmail   = ctx["gmail"]
    root    = ctx["root_folder"]

    name    = (entities.get("person_name")  or "").strip()
    body    = (entities.get("message_body") or "").strip()
    subject = (entities.get("email_subject") or "").strip()

    # Resolve recipient
    if not name:
        speaker.speak("Who should I send the email to?", signals=signals)
        name = listen_for_speech(stt) or ""
    if not name:
        speaker.speak("Didn't catch the recipient.", signals=signals)
        return

    to_addr = _resolve_email(name, root)
    if not to_addr:
        speaker.speak(
            f"I don't have an email address for '{name}'. "
            "Add them to data/email_contacts.json and try again.",
            signals=signals,
        )
        return

    # Get message content
    if not body:
        speaker.speak(f"What should the email say?", signals=signals)
        body = listen_for_speech(stt) or ""
    if not body:
        speaker.speak("Didn't catch the message. Email cancelled.", signals=signals)
        return

    # Get subject if not provided
    if not subject:
        speaker.speak("What's the subject? Or say 'skip' to use a default.", signals=signals)
        subject_resp = listen_for_speech(stt) or ""
        if subject_resp.lower().strip() in ("skip", "no", "none", "default"):
            subject = "Hey"
        else:
            subject = subject_resp or "Hey"

    # Draft via LLM for polish
    speaker.speak(f"Drafting email to {name}. One moment.", signals=signals)
    draft = brain.compose_reply(
        {"sender": to_addr, "subject": subject},
        body,
    )

    # Read draft aloud — interruptible=False prevents the interrupt listener from
    # holding the mic open and racing with the confirmation listen() that follows.
    speaker.speak(f"Here's the draft: {draft}. Shall I send it?",
                  signals=signals, interruptible=False)

    # Recalibrate mic after TTS (dynamic_energy_threshold inflates threshold during playback)
    confirm = listen_for_confirmation(stt)

    # If timeout (no response), ask once more
    if confirm is None:
        speaker.speak("Should I send it? Say yes or no.", signals=signals, interruptible=False)
        confirm = listen_for_confirmation(stt)

    _SEND_WORDS    = {"yes", "send", "go ahead", "sure", "do it", "confirm",
                      "yeah", "yep", "okay", "ok", "alright", "absolutely",
                      "please", "do that", "send that", "send it", "send the email"}
    _CANCEL_WORDS  = {"no", "cancel", "don't", "nope", "never mind", "forget it",
                      "abort", "discard", "don't send"}

    low_confirm = (confirm or "").lower()
    if any(w in low_confirm for w in _SEND_WORDS):
        success = gmail.send_email(to_addr, subject, draft)
        if success:
            speaker.speak(f"Email sent to {name}.", signals=signals)
        else:
            speaker.speak("Failed to send. Check your Gmail credentials in dot env.", signals=signals)
    elif any(w in low_confirm for w in _CANCEL_WORDS) or confirm is None:
        speaker.speak("Email cancelled.", signals=signals)
    else:
        # Ambiguous response — ask one final time
        speaker.speak(f"I heard '{confirm}'. Say send to confirm or cancel to discard.",
                      signals=signals, interruptible=False)
        final = listen_for_confirmation(stt) or ""
        if any(w in final.lower() for w in _SEND_WORDS):
            success = gmail.send_email(to_addr, subject, draft)
            speaker.speak(f"Email sent to {name}." if success
                          else "Failed to send. Check your credentials.", signals=signals)
        else:
            speaker.speak("Email cancelled.", signals=signals)


def handle_draft_reply(ctx, entities, original_email):
    """Dictate, draft, confirm, and send an email reply."""
    stt = ctx["stt"]
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    brain = ctx["brain"]
    gmail = ctx["gmail"]

    message_body = entities.get("message_body")
    if not message_body:
        speaker.speak("What should the reply say?", signals=signals)
        message_body = listen_for_speech(stt)
        if not message_body:
            speaker.speak("Didn't catch that. Reply cancelled.", signals=signals)
            return

    drafted = brain.compose_reply(original_email, message_body)
    print(f"Draft: {drafted}")

    speaker.speak(f"Here's the draft. {drafted}. Shall I send this?",
                  signals=signals, interruptible=False)
    confirm = listen_for_confirmation(stt)

    if confirm is None:
        speaker.speak("Should I send it? Say yes or no.", signals=signals, interruptible=False)
        confirm = listen_for_confirmation(stt)

    _SEND_WORDS = {"yes", "send", "go ahead", "sure", "do it", "confirm",
                   "yeah", "yep", "okay", "ok", "alright", "absolutely",
                   "please", "do that", "send that", "send it"}

    if confirm and any(w in confirm.lower() for w in _SEND_WORDS):
        success = gmail.reply_to_email(original_email, drafted)
        if success:
            speaker.speak("Reply sent.", signals=signals)
        else:
            speaker.speak("Failed to send. Please check your connection.", signals=signals)
    else:
        speaker.speak("Reply cancelled.", signals=signals)


def handle_open_app(ctx, entities):
    """Launch a desktop application by name."""
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    launcher = ctx["launcher"]

    app_name = entities.get("app_name", "").strip()
    if not app_name:
        speaker.speak("Which app should I open?", signals=signals)
        app_name = listen_for_speech(ctx["stt"]) or ""
        if not app_name:
            speaker.speak("Couldn't catch the app name.", signals=signals)
            return

    success, matched = launcher.launch(app_name)
    if success:
        speaker.speak(f"Opening {matched}.", signals=signals)
    else:
        speaker.speak(f"Couldn't find {app_name} on your system.", signals=signals)


def handle_close_app(ctx, entities):
    """Terminate a running application by name."""
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    launcher = ctx["launcher"]

    app_name = entities.get("app_name", "").strip()
    if not app_name:
        speaker.speak("Which app should I close?", signals=signals)
        app_name = listen_for_speech(ctx["stt"]) or ""
        if not app_name:
            speaker.speak("Couldn't catch the app name.", signals=signals)
            return

    success, proc_name = launcher.close(app_name)
    if success:
        speaker.speak(f"Closed {app_name}.", signals=signals)
    else:
        speaker.speak(f"{app_name} doesn't appear to be running.", signals=signals)


# ---------------------------------------------------------------------------
# Productivity handlers
# ---------------------------------------------------------------------------

def handle_add_task(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    stt = ctx["stt"];         tasks   = ctx["tasks"]

    title = (entities.get("event_title") or "").strip()
    if not title:
        low = user_text.lower()
        for pfx in ("add task:", "add task", "add a task:", "add a task",
                    "remind me to", "create task:", "create task"):
            if pfx in low:
                title = user_text[low.index(pfx) + len(pfx):].strip(" :")
                break
    if not title:
        speaker.speak("What's the task?", signals=signals)
        title = listen_for_speech(stt) or ""
    if not title:
        speaker.speak("Didn't catch the task name.", signals=signals)
        return

    due = (entities.get("datetime_str") or "").strip() or None
    tasks.add_task(title, due_date=due)
    msg = f"Added: {title}" + (f", due {due}." if due else ".")
    speaker.speak(msg, signals=signals)


def handle_complete_task(ctx, entities):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    stt = ctx["stt"];         tasks   = ctx["tasks"]

    fragment = (entities.get("event_title") or "").strip()
    if not fragment:
        speaker.speak("Which task is done?", signals=signals)
        fragment = listen_for_speech(stt) or ""
    if not fragment:
        speaker.speak("Didn't catch that.", signals=signals)
        return

    matched = tasks.complete_by_title(fragment)
    if matched:
        speaker.speak(f"Marked done: {matched}.", signals=signals)
    else:
        speaker.speak("Couldn't find a matching task.", signals=signals)


def handle_list_tasks(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    tasks   = ctx["tasks"]

    pending = tasks.get_pending()
    if not pending:
        speaker.speak("No pending tasks. You're all caught up!", signals=signals)
        return
    if len(pending) == 1:
        t = pending[0]
        msg = f"You have one task: {t['title']}"
        if t.get("due_date"):
            msg += f", due {t['due_date']}"
        speaker.speak(msg + ".", signals=signals)
        return
    names = ", ".join(t["title"] for t in pending[:4])
    suffix = f" and {len(pending) - 4} more" if len(pending) > 4 else ""
    speaker.speak(f"You have {len(pending)} tasks: {names}{suffix}.", signals=signals)


def handle_delete_task(ctx, entities):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    stt = ctx["stt"];         tasks   = ctx["tasks"]

    fragment = (entities.get("event_title") or "").strip()
    if not fragment:
        speaker.speak("Which task should I remove?", signals=signals)
        fragment = listen_for_speech(stt) or ""
    if not fragment:
        speaker.speak("Didn't catch that.", signals=signals)
        return

    matched = tasks.delete_by_title(fragment)
    if matched:
        speaker.speak(f"Removed: {matched}.", signals=signals)
    else:
        speaker.speak("Couldn't find that task.", signals=signals)


def handle_start_timer(ctx, entities, pomodoro):
    speaker = ctx["speaker"]; signals = ctx["signals"]

    duration_str = (entities.get("duration_str") or "").lower()
    mins = 25  # default pomodoro
    m = re.search(r"(\d+)\s*(?:min|minute)", duration_str)
    if m:
        mins = int(m.group(1))
    else:
        m = re.search(r"(\d+)\s*(?:hr|hour)", duration_str)
        if m:
            mins = int(m.group(1)) * 60

    def _on_done(total):
        speaker.speak(
            f"Focus session complete! You stayed focused for {total} minutes. "
            "Great work — time for a well-earned break.",
            signals=signals,
        )

    pomodoro.start(mins, on_done=_on_done)
    speaker.speak(
        f"Starting a {mins}-minute focus session. I'll let you know when it's done.",
        signals=signals,
    )


def handle_stop_timer(ctx, pomodoro):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    if pomodoro.is_running:
        elapsed = pomodoro.total_minutes - pomodoro.remaining_seconds // 60
        pomodoro.cancel()
        speaker.speak(f"Timer stopped. You focused for about {elapsed} minutes.", signals=signals)
    else:
        speaker.speak("No timer is currently running.", signals=signals)


def handle_timer_status(ctx, pomodoro):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    if not pomodoro.is_running:
        speaker.speak("No active timer right now.", signals=signals)
        return
    rem = pomodoro.remaining_seconds
    mins, secs = rem // 60, rem % 60
    if mins > 0:
        speaker.speak(f"{mins} minutes and {secs} seconds remaining.", signals=signals)
    else:
        speaker.speak(f"{secs} seconds remaining.", signals=signals)


def handle_start_focus(ctx, entities, focus):
    speaker = ctx["speaker"]; signals = ctx["signals"]

    duration_str = (entities.get("duration_str") or "").lower()
    mins = None
    m = re.search(r"(\d+)\s*(?:hr|hour)", duration_str)
    if m:
        mins = int(m.group(1)) * 60
    else:
        m = re.search(r"(\d+)\s*(?:min|minute)", duration_str)
        if m:
            mins = int(m.group(1))

    def _on_end():
        speaker.speak("Focus session ended. Welcome back!", signals=signals)

    focus.start(minutes=mins, on_done=_on_end)
    dur_label = f"for {mins} minutes " if mins else ""
    speaker.speak(
        f"Focus mode on. {dur_label}Distraction apps closed. "
        "You've got this — stay in the zone.",
        signals=signals,
    )


def handle_end_focus(ctx, focus):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    if focus.is_active:
        focus.end()
        speaker.speak("Focus mode off. Good work!", signals=signals)
    else:
        speaker.speak("Focus mode isn't active right now.", signals=signals)


def handle_clipboard_summarise(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    brain   = ctx["brain"]

    text = _get_clipboard()
    if not text:
        speaker.speak("Clipboard is empty or I couldn't read it.", signals=signals)
        return
    speaker.speak("One moment, reading what you copied.", signals=signals)
    summary = brain.summarise_clipboard(text)
    print(f"Atlas [Clipboard Summary]: {summary}")
    speaker.speak(summary, signals=signals)


def handle_clipboard_improve(ctx, entities):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    brain   = ctx["brain"]

    text = _get_clipboard()
    if not text:
        speaker.speak("Clipboard is empty or I couldn't read it.", signals=signals)
        return

    style = (entities.get("message_body") or "").strip()
    speaker.speak("Improving your text. One moment.", signals=signals)
    improved = brain.improve_clipboard(text, style_hint=style)
    _set_clipboard(improved)
    print(f"Atlas [Clipboard Improve]: done ({len(improved)} chars)")
    speaker.speak(
        "Done. The improved version is in your clipboard — just paste it.",
        signals=signals,
    )


# ---------------------------------------------------------------------------
# Health reminders
# ---------------------------------------------------------------------------

def _parse_interval_mins(duration_str: str):
    """Extract interval in minutes from phrases like 'every hour', 'every 45 minutes'."""
    s = duration_str.lower()
    if "every hour" in s or "hourly" in s:
        return 60
    if "every half" in s:
        return 30
    m = re.search(r"every\s+(\d+(?:\.\d+)?)\s*(?:hr|hour)", s)
    if m:
        return max(5, int(float(m.group(1)) * 60))
    m = re.search(r"every\s+(\d+)\s*(?:min|minute)", s)
    if m:
        return max(5, int(m.group(1)))
    m = re.search(r"(\d+)\s*(?:min|minute)", s)
    if m:
        return max(5, int(m.group(1)))
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:hr|hour)", s)
    if m:
        return max(5, int(float(m.group(1)) * 60))
    return None


def _parse_hhmm(time_str: str):
    """Parse a time phrase like 'at 8am', '11:30 pm' → (hour, minute) or None."""
    try:
        import dateparser
        t = dateparser.parse(time_str)
        if t:
            return t.hour, t.minute
    except Exception:
        pass
    return None


_WATER_WORDS  = ("water", "drink", "hydrat")
_BREAK_WORDS  = ("break", "rest", "eye", "screen", "posture", "stretch", "20-20")
_SLEEP_WORDS  = ("sleep", "bed", "bedtime", "wind down", "midnight")


def handle_set_reminder(ctx, entities, reminders):
    speaker  = ctx["speaker"]; signals = ctx["signals"]
    stt      = ctx["stt"]

    what         = (entities.get("event_title")  or "").strip().lower()
    duration_str = (entities.get("duration_str") or "").strip()
    time_str     = (entities.get("datetime_str") or "").strip()

    # ── Water reminder ──────────────────────────────────────
    if any(w in what for w in _WATER_WORDS):
        mins = _parse_interval_mins(duration_str) or 60
        reminders.add_interval(
            "water",
            "Time to drink some water! Staying hydrated keeps you sharp.",
            mins,
        )
        speaker.speak(f"Water reminder on. I'll nudge you every {mins} minutes.", signals=signals)
        return

    # ── Break / eye reminder ────────────────────────────────
    if any(w in what for w in _BREAK_WORDS):
        mins = _parse_interval_mins(duration_str) or 45
        reminders.add_interval(
            "break",
            "Break time! Stand up, stretch, and look at something 20 feet away for 20 seconds. "
            "Your eyes and back will thank you.",
            mins,
        )
        speaker.speak(f"Break reminder on every {mins} minutes.", signals=signals)
        return

    # ── Sleep / bedtime reminder ────────────────────────────
    if any(w in what for w in _SLEEP_WORDS):
        hm = _parse_hhmm(time_str) if time_str else None
        h, m = hm if hm else (23, 0)
        reminders.add_scheduled(
            "sleep",
            "It's your bedtime! Put the screens away, wind down, "
            "and get the rest you deserve.",
            h, m,
        )
        speaker.speak(
            f"Bedtime reminder set for {h % 12 or 12}:{'00' if m == 0 else m:02d} "
            f"{'AM' if h < 12 else 'PM'} every night.",
            signals=signals,
        )
        return

    # ── Named medication / custom reminder at a specific time ─
    if time_str and what:
        hm = _parse_hhmm(time_str)
        if hm:
            h, m = hm
            name_key = what.replace(" ", "_")[:20]
            msg = f"Reminder: time to take your {what}."
            reminders.add_scheduled(name_key, msg, h, m)
            speaker.speak(
                f"Daily reminder set — I'll remind you about {what} at "
                f"{h % 12 or 12}:{'00' if m == 0 else m:02d} "
                f"{'AM' if h < 12 else 'PM'} every day.",
                signals=signals,
            )
            return

    # ── Fallback — ask what they need ──────────────────────
    speaker.speak(
        "What should I remind you about? For example: "
        "'water every hour', 'break every 45 minutes', or 'vitamin D at 8am'.",
        signals=signals,
    )


def handle_stop_reminder(ctx, entities, user_text, reminders):
    speaker = ctx["speaker"]; signals = ctx["signals"]

    what = (entities.get("event_title") or entities.get("message_body") or "").strip().lower()

    if not what or any(w in what for w in ("all", "every", "everything")):
        reminders.clear_all()
        speaker.speak("All reminders cleared.", signals=signals)
        return

    # Map common words → canonical names
    if any(w in what for w in _WATER_WORDS):
        key = "water"
    elif any(w in what for w in _BREAK_WORDS):
        key = "break"
    elif any(w in what for w in _SLEEP_WORDS):
        key = "sleep"
    else:
        # Try exact match first, then substring match against active names
        key = what
        if key not in reminders.active_names:
            for name in reminders.active_names:
                if what in name:
                    key = name
                    break

    if reminders.remove(key):
        speaker.speak(f"{key.replace('_', ' ').capitalize()} reminder stopped.", signals=signals)
    else:
        speaker.speak(f"No active reminder found for '{key}'.", signals=signals)


def handle_list_reminders(ctx, reminders):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    items = reminders.list_all()
    if not items:
        speaker.speak("No active reminders right now.", signals=signals)
        return
    if len(items) == 1:
        speaker.speak(f"You have one active reminder: {items[0]}.", signals=signals)
        return
    joined = ", ".join(items)
    speaker.speak(f"You have {len(items)} reminders: {joined}.", signals=signals)


# ---------------------------------------------------------------------------
# Information on demand
# ---------------------------------------------------------------------------

def handle_calculate(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    expression = (entities.get("message_body") or user_text).strip()
    result = ctx["brain"].calculate(expression)
    print(f"Atlas [Calc]: {expression} → {result}")
    speaker.speak(result, signals=signals)


def handle_convert(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    query = (entities.get("message_body") or user_text).strip()
    result = ctx["brain"].convert_units(query)
    print(f"Atlas [Convert]: {result}")
    speaker.speak(result, signals=signals)


def handle_weather(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    city = (entities.get("message_body") or "").strip()
    if not city:
        city = os.getenv("DEFAULT_CITY", "Chennai")

    speaker.speak("Checking the weather.", signals=signals)
    data = get_weather(city)
    if not data:
        speaker.speak(f"Couldn't get weather for {city}. Check your internet connection.", signals=signals)
        return

    msg = (
        f"In {data['city']}, it's {data['temp']}°C and {data['condition']}. "
        f"Feels like {data['feels_like']}°C. "
        f"High of {data['high']}°C, low of {data['low']}°C"
    )
    if data.get("rain_chance") is not None:
        msg += f", with a {data['rain_chance']}% chance of rain"
    if data.get("humidity") is not None:
        msg += f". Humidity {data['humidity']}%"
    if data.get("wind_kmh"):
        msg += f", wind at {data['wind_kmh']} km/h"
    msg += "."
    print(f"Atlas [Weather]: {msg}")
    speaker.speak(msg, signals=signals)


def handle_web_search(ctx, entities, user_text):
    import webbrowser
    from urllib.parse import quote as url_quote
    speaker = ctx["speaker"]; signals = ctx["signals"]

    query = (entities.get("message_body") or "").strip()
    if not query:
        low = user_text.lower()
        for pfx in ("search for", "search", "google", "look up", "find"):
            if pfx in low:
                query = user_text[low.index(pfx) + len(pfx):].strip(" :")
                break
    if not query:
        speaker.speak("What should I search for?", signals=signals)
        query = listen_for_speech(ctx["stt"]) or ""
    if not query:
        return

    webbrowser.open(f"https://www.google.com/search?q={url_quote(query)}")
    speaker.speak(f"Searching for {query}.", signals=signals)


def handle_define(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]

    word = (entities.get("message_body") or "").strip()
    if not word:
        low = user_text.lower()
        for pfx in ("define ", "definition of ", "what does ", "meaning of ", "what is "):
            if pfx in low:
                word = user_text[low.index(pfx) + len(pfx):].strip(" :?").replace(" mean", "").strip()
                break
    if not word:
        speaker.speak("Which word should I define?", signals=signals)
        word = listen_for_speech(ctx["stt"]) or ""
    if not word:
        return

    definition = define_word(word)
    if definition:
        print(f"Atlas [Define]: {definition}")
        speaker.speak(definition, signals=signals)
    else:
        # Fall back to LLM if dictionary API misses it
        result = ctx["brain"].think(f"Give a short, clear spoken definition of the word: {word}")
        speaker.speak(result, signals=signals)


def handle_type_text(ctx, entities):
    """Type the extracted text at the current cursor position using pynput."""
    speaker = ctx["speaker"]
    signals = ctx["signals"]

    text = (entities.get("message_body") or "").strip()
    if not text:
        speaker.speak("What should I type?", signals=signals)
        text = listen_for_speech(ctx["stt"]) or ""
        if not text:
            speaker.speak("Didn't catch that.", signals=signals)
            return

    try:
        from pynput.keyboard import Controller
        kb = Controller()
        time.sleep(0.3)   # brief pause so the focus stays on the target window
        kb.type(text)
        speaker.speak("Done.", signals=signals)
    except Exception as e:
        print(f"Type error: {e}")
        speaker.speak("Couldn't type that.", signals=signals)


def handle_log_health(ctx, user_text: str):
    """Parse a natural-language health log, store it, and confirm what was recorded."""
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    brain   = ctx["brain"]
    tracker = ctx["health"]

    speaker.speak("Logging your health data. One moment.", signals=signals)
    entry = brain.parse_health_log(user_text)

    if not entry:
        speaker.speak("I couldn't extract any health data from that. Try saying something like: 'I walked 8,000 steps, drank 2 litres of water, and slept 7 hours.'", signals=signals)
        return

    tracker.log_entry(entry)

    # Build a readable confirmation
    parts = []
    if entry.get("steps"):       parts.append(f"{entry['steps']:,} steps")
    if entry.get("water_ml"):    parts.append(f"{entry['water_ml'] / 1000:.1f} litres of water")
    if entry.get("sleep_hours"): parts.append(f"{entry['sleep_hours']} hours of sleep")
    if entry.get("meals"):       parts.append(f"{entry['meals']} meals")
    if entry.get("workout"):
        wt = entry.get("workout_type", "a workout")
        parts.append(wt)
    if entry.get("heart_rate_avg"): parts.append(f"heart rate {entry['heart_rate_avg']} bpm")
    if entry.get("spo2"):           parts.append(f"SpO2 {entry['spo2']}%")
    if entry.get("blood_sugar"):    parts.append(f"blood sugar {entry['blood_sugar']} mg/dL")

    summary = ", ".join(parts) if parts else "the provided data"
    speaker.speak(f"Logged: {summary}. All saved.", signals=signals)
    print(f"HealthTracker logged: {entry}")


def handle_health_summary(ctx):
    """Read back today's health stats and a short 7-day trend."""
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    tracker = ctx["health"]

    today = tracker.get_entry()
    analytics = tracker.compute_analytics(days=7)

    if not today:
        speaker.speak("No health data logged for today yet. Tell me about your activity and I'll record it.", signals=signals)
        return

    today_str  = tracker.format_entry(today)
    trends_str = ""
    if analytics:
        parts = []
        if analytics.get("avg_steps"):       parts.append(f"average {analytics['avg_steps']:,} steps")
        if analytics.get("avg_sleep_hours"): parts.append(f"{analytics['avg_sleep_hours']} h sleep")
        if analytics.get("avg_water_ml"):    parts.append(f"{analytics['avg_water_ml'] / 1000:.1f} L water")
        if analytics.get("workout_frequency"): parts.append(f"worked out {analytics['workout_frequency']}")
        if parts:
            trends_str = f" Over the past {analytics.get('period_days', 7)} days: {', '.join(parts)}."

    speaker.speak(f"Here's your health summary for today. {today_str}.{trends_str}", signals=signals)


def handle_health_advice(ctx):
    """Fetch analytics and patterns, then deliver personalised spoken health advice."""
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    brain   = ctx["brain"]
    tracker = ctx["health"]

    speaker.speak("Analysing your health data. One moment.", signals=signals)

    today      = tracker.get_entry()
    analytics  = tracker.compute_analytics(days=7)
    patterns   = tracker.find_patterns(days=30)
    today_str  = tracker.format_entry(today) if today else "No data for today yet."

    advice = brain.generate_health_advice(today_str, analytics, patterns)
    print(f"Atlas [Health Advice]: {advice}")
    speaker.speak(advice, signals=signals)


def handle_emotional_support(ctx, user_text):
    """Route to Atlas's empathetic companion mode."""
    speaker = ctx["speaker"]
    signals = ctx["signals"]
    brain   = ctx["brain"]

    response = brain.emotional_chat(user_text)
    print(f"Atlas [Emotional]: {response}")
    speaker.speak(response, signals=signals)


def handle_daily_summary(ctx):
    """Fetch today's calendar and emails, then deliver a spoken morning briefing."""
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    brain   = ctx["brain"]
    gcal    = ctx["gcal"]
    gmail   = ctx["gmail"]

    speaker.speak("Pulling up your day. One moment.", signals=signals)

    # --- Calendar events ---
    raw_events = gcal.get_today_events()
    events_for_llm = []
    for ev in raw_events:
        try:
            start_dt = datetime.fromisoformat(ev["start"])
            end_dt   = datetime.fromisoformat(ev["end"])
            dur_min  = int((end_dt - start_dt).total_seconds() / 60)
            events_for_llm.append({
                "title":          ev["title"],
                "start_label":    start_dt.strftime("%I:%M %p").lstrip("0"),
                "end_label":      end_dt.strftime("%I:%M %p").lstrip("0"),
                "duration_label": _fmt_duration(dur_min),
            })
        except Exception:
            events_for_llm.append({
                "title":          ev["title"],
                "start_label":    ev.get("start", "?"),
                "end_label":      ev.get("end", "?"),
                "duration_label": "",
            })

    # --- Emails (lightweight: just sender + subject, no body fetch) ---
    try:
        emails_raw = gmail.fetch_today_emails(max_count=10)
        emails_for_llm = [{"sender": e["sender"], "subject": e["subject"]} for e in emails_raw]
        ctx["email_context"] = emails_raw
    except Exception:
        emails_for_llm = []

    briefing = brain.generate_daily_briefing(events_for_llm, emails_for_llm)
    print(f"Atlas [Daily Briefing]: {briefing}")
    speaker.speak(briefing, signals=signals)


def handle_interrupt_command(text, current_email, ctx):
    """Route a mid-speech interrupt command using the current email as context."""
    router = ctx["router"]
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    brain = ctx["brain"]

    intent_data = router.classify(text)
    intent = intent_data.get("intent")
    entities = intent_data.get("entities", {})

    if intent == "schedule_event":
        handle_schedule(ctx, entities, current_email)
    elif intent == "draft_reply":
        handle_draft_reply(ctx, entities, current_email)
    elif intent == "continue_reading":
        pass
    else:
        resp = brain.think(text)
        print(f"Atlas: {resp}")
        speaker.speak(resp, signals=signals)


def handle_email_summary(ctx):
    """Fetch today's emails and read summaries aloud, one at a time, with live interrupt support."""
    stt = ctx["stt"]
    signals = ctx["signals"]
    speaker = ctx["speaker"]
    brain = ctx["brain"]
    router = ctx["router"]
    gmail = ctx["gmail"]

    speaker.speak("Fetching your emails. Give me a moment.", signals=signals)
    emails = gmail.fetch_today_emails()
    ctx["email_context"] = emails

    if not emails:
        speaker.speak("Your inbox is clear today. No emails to report.", signals=signals)
        return

    speaker.speak(f"You have {len(emails)} {'email' if len(emails) == 1 else 'emails'} today. Beginning briefing.", signals=signals)

    for i, em in enumerate(emails):
        ctx["active_email"] = em
        summary = brain.summarize_single_email(em)
        print(f"Atlas [Email {i+1}/{len(emails)}]: {summary}")

        interrupted = speaker.speak(summary, signals=signals, interruptible=True)

        if interrupted:
            print(f"You (interrupt): {interrupted}")
            intent_data = router.classify(interrupted)
            interrupt_intent = intent_data.get("intent")

            if interrupt_intent == "interrupt_pause":
                speaker.speak("Paused. What would you like to do?", signals=signals)
                sub_cmd = listen_for_speech(stt)
                if sub_cmd:
                    handle_interrupt_command(sub_cmd, em, ctx)
            else:
                handle_interrupt_command(interrupted, em, ctx)

            # After handling interrupt, ask whether to continue (unless last email)
            if i < len(emails) - 1:
                speaker.speak("Continue with the remaining emails?", signals=signals)
                response = listen_for_speech(stt)
                if response and not any(w in response.lower() for w in
                                        ["yes", "continue", "go ahead", "proceed", "next", "sure"]):
                    speaker.speak("Briefing paused. Let me know when you're ready to continue.", signals=signals)
                    return

        time.sleep(0.3)

    speaker.speak("That's all for today's emails.", signals=signals)


# ---------------------------------------------------------------------------
# System & media integration handlers
# ---------------------------------------------------------------------------

def handle_media_play_pause(ctx):
    play_pause()
    ctx["speaker"].speak("Done.", signals=ctx["signals"])


def handle_media_next(ctx):
    next_track()
    ctx["speaker"].speak("Next track.", signals=ctx["signals"])


def handle_media_prev(ctx):
    prev_track()
    ctx["speaker"].speak("Going back.", signals=ctx["signals"])


def handle_volume_up(ctx):
    volume_up(steps=5)
    ctx["speaker"].speak("Volume up.", signals=ctx["signals"])


def handle_volume_down(ctx):
    volume_down(steps=5)
    ctx["speaker"].speak("Volume down.", signals=ctx["signals"])


def handle_volume_mute(ctx):
    media_mute()
    ctx["speaker"].speak("Muted.", signals=ctx["signals"])


def handle_volume_set(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    raw = (entities.get("message_body") or user_text or "").strip()
    m = re.search(r'(\d+)', raw)
    if not m:
        speaker.speak("What percentage should I set the volume to?", signals=signals)
        raw = listen_for_speech(ctx["stt"]) or ""
        m = re.search(r'(\d+)', raw)
    if m:
        pct = max(0, min(100, int(m.group(1))))
        set_volume_percent(pct)
        speaker.speak(f"Volume set to {pct} percent.", signals=signals)
    else:
        speaker.speak("Couldn't catch the percentage.", signals=signals)


def handle_screen_lock(ctx):
    ctx["speaker"].speak("Locking your screen.", signals=ctx["signals"])
    time.sleep(0.4)
    ctypes.windll.user32.LockWorkStation()


def handle_system_shutdown(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    speaker.speak("Are you sure you want to shut down?", signals=signals)
    confirm = listen_for_speech(stt)
    if confirm and any(w in confirm.lower() for w in
                       ["yes", "sure", "do it", "go ahead", "confirm", "shutdown", "shut down"]):
        speaker.speak("Shutting down. Goodbye.", signals=signals)
        subprocess.Popen(["shutdown", "/s", "/t", "10"])
    else:
        speaker.speak("Shutdown cancelled.", signals=signals)


def handle_system_restart(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    speaker.speak("Restart your computer?", signals=signals)
    confirm = listen_for_speech(stt)
    if confirm and any(w in confirm.lower() for w in
                       ["yes", "sure", "do it", "go ahead", "confirm", "restart", "reboot"]):
        speaker.speak("Restarting. See you on the other side.", signals=signals)
        subprocess.Popen(["shutdown", "/r", "/t", "10"])
    else:
        speaker.speak("Restart cancelled.", signals=signals)


# ---------------------------------------------------------------------------
# Integration handlers — WhatsApp, Google Drive, GitHub, Notion
# ---------------------------------------------------------------------------

def handle_whatsapp_send(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    wa = ctx["integrations"]["whatsapp"]

    name    = (entities.get("person_name")  or "").strip()
    message = (entities.get("message_body") or "").strip()

    if not name:
        speaker.speak("Who should I message on WhatsApp?", signals=signals)
        name = listen_for_speech(stt) or ""
    if not name:
        speaker.speak("Didn't catch the name.", signals=signals)
        return

    if not message:
        speaker.speak(f"What should I tell {name}?", signals=signals)
        message = listen_for_speech(stt) or ""
    if not message:
        speaker.speak("Didn't catch the message.", signals=signals)
        return

    success, feedback = wa.send(name, message)
    speaker.speak(feedback, signals=signals)


def handle_drive_search(ctx, entities, user_text):
    import webbrowser as _wb
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    drive = ctx["integrations"]["drive"]

    if not drive.is_connected:
        speaker.speak(
            "Google Drive isn't connected. Make sure credentials.json is in the Atlas folder "
            "and try again.", signals=signals,
        )
        return

    query = (entities.get("message_body") or "").strip()
    if not query:
        low = user_text.lower()
        for pfx in ("find my", "search drive for", "search google drive for",
                    "find", "look for", "search for"):
            if pfx in low:
                query = user_text[low.index(pfx) + len(pfx):].strip().rstrip(" on drive")
                break
    if not query:
        speaker.speak("What should I search for in Drive?", signals=signals)
        query = listen_for_speech(stt) or ""
    if not query:
        return

    speaker.speak(f"Searching Drive for '{query}'.", signals=signals)
    results = drive.search(query)

    if not results:
        speaker.speak(f"Nothing found in Drive matching '{query}'.", signals=signals)
        return

    if len(results) == 1:
        r = results[0]
        speaker.speak(
            f"Found one file: {r['name']}, last modified {r['modified']}. Opening it.",
            signals=signals,
        )
        drive.open_file(r["link"])
    else:
        names = ", ".join(r["name"] for r in results[:3])
        extra = f" and {len(results) - 3} more" if len(results) > 3 else ""
        speaker.speak(
            f"Found {len(results)} files: {names}{extra}. Opening the most recent one.",
            signals=signals,
        )
        drive.open_file(results[0]["link"])


def handle_github_prs(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    gh = ctx["integrations"]["github"]

    if not gh.is_configured:
        speaker.speak(
            "GitHub isn't set up yet. Add GITHUB_TOKEN and GITHUB_USERNAME to your .env file.",
            signals=signals,
        )
        return

    speaker.speak("Checking your open pull requests.", signals=signals)
    prs = gh.my_open_prs()
    if not prs:
        speaker.speak("No open pull requests found.", signals=signals)
        return

    if len(prs) == 1:
        speaker.speak(f"You have one open PR: {prs[0]['title']} in {prs[0]['repo']}.", signals=signals)
    else:
        titles = "; ".join(f"{p['title']} in {p['repo']}" for p in prs[:3])
        extra  = f" and {len(prs) - 3} more" if len(prs) > 3 else ""
        speaker.speak(f"You have {len(prs)} open PRs: {titles}{extra}.", signals=signals)
    if prs[0].get("url"):
        gh.open_in_browser(prs[0]["url"])


def handle_github_issues(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    gh = ctx["integrations"]["github"]

    if not gh.is_configured:
        speaker.speak("GitHub isn't configured. Add GITHUB_TOKEN to your .env.", signals=signals)
        return

    speaker.speak("Fetching your assigned issues.", signals=signals)
    issues = gh.my_open_issues()
    if not issues:
        speaker.speak("No open issues assigned to you right now.", signals=signals)
        return

    if len(issues) == 1:
        speaker.speak(f"One issue: {issues[0]['title']} in {issues[0]['repo']}.", signals=signals)
    else:
        titles = "; ".join(f"{i['title']}" for i in issues[:3])
        extra  = f" and {len(issues) - 3} more" if len(issues) > 3 else ""
        speaker.speak(f"{len(issues)} issues assigned to you: {titles}{extra}.", signals=signals)


def handle_github_create_issue(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    gh = ctx["integrations"]["github"]

    if not gh.is_configured:
        speaker.speak(
            "GitHub isn't configured. Add GITHUB_TOKEN, GITHUB_USERNAME, and "
            "GITHUB_DEFAULT_REPO to your .env file.",
            signals=signals,
        )
        return

    title = (entities.get("event_title") or "").strip()
    body  = (entities.get("message_body") or "").strip()

    if not title:
        speaker.speak("What's the issue title?", signals=signals)
        title = listen_for_speech(stt) or ""
    if not title:
        speaker.speak("Didn't catch the title. Cancelled.", signals=signals)
        return

    speaker.speak(f"Creating issue: {title}.", signals=signals)
    url = gh.create_issue(title, body)
    if url:
        speaker.speak(f"Issue created. Opening it in your browser.", signals=signals)
        gh.open_in_browser(url)
    else:
        speaker.speak(
            "Couldn't create the issue. Check GITHUB_DEFAULT_REPO in your .env file.",
            signals=signals,
        )


def handle_notion_add_note(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    notion = ctx["integrations"]["notion"]

    if not notion.is_configured:
        speaker.speak(
            "Notion isn't set up. Add NOTION_TOKEN and NOTION_DEFAULT_PAGE_ID to your .env.",
            signals=signals,
        )
        return

    content = (entities.get("message_body") or "").strip()
    title   = (entities.get("event_title")  or "").strip()

    if not content and not title:
        speaker.speak("What should I add to Notion?", signals=signals)
        content = listen_for_speech(stt) or ""
    if not content:
        content = title

    if not content:
        speaker.speak("Didn't catch the note. Cancelled.", signals=signals)
        return

    speaker.speak("Adding to Notion.", signals=signals)
    success = notion.add_note(title, content)
    if success:
        speaker.speak(f"Done. Note added to Notion.", signals=signals)
    else:
        speaker.speak("Couldn't add to Notion. Check your token and page ID.", signals=signals)


def handle_spotify_play(ctx, entities, user_text):
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    sp = ctx["integrations"]["spotify"]

    if not sp.is_configured:
        speaker.speak(
            "Spotify isn't set up yet. Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET "
            "to your .env file.", signals=signals,
        )
        return

    query = (entities.get("message_body") or "").strip()
    if not query:
        # Strip common prefixes from raw text
        low = user_text.lower()
        for pfx in ("play ", "put on ", "start playing "):
            if pfx in low:
                query = user_text[low.index(pfx) + len(pfx):]
                for sfx in (" on spotify", " in spotify"):
                    query = query.replace(sfx, "").replace(sfx.title(), "")
                query = query.strip()
                break
    if not query:
        speaker.speak("What should I play on Spotify?", signals=signals)
        query = listen_for_speech(stt) or ""
    if not query:
        return

    speaker.speak(f"Searching for {query}.", signals=signals)
    success, name = sp.search_and_play(query)

    if success:
        speaker.speak(f"Now playing {name}.", signals=signals)
    elif name == "no_device":
        # Spotify isn't open or no active device — launch it and retry once
        speaker.speak("Opening Spotify.", signals=signals)
        import subprocess as _sp
        try:
            _sp.Popen(["spotify"], shell=True)
        except Exception:
            pass
        import time as _time
        _time.sleep(4)
        success2, name2 = sp.search_and_play(query)
        if success2:
            speaker.speak(f"Now playing {name2}.", signals=signals)
        else:
            speaker.speak("Spotify opened but couldn't start playback. Try saying play again.", signals=signals)
    elif name == "premium_required":
        speaker.speak(
            "Spotify playback control requires a Premium account.", signals=signals,
        )
    elif name == "nothing_found":
        speaker.speak(f"Couldn't find {query} on Spotify.", signals=signals)
    elif name == "not_configured":
        speaker.speak("Spotify isn't authorized yet. Check your dot env and try again.", signals=signals)
    else:
        speaker.speak("Spotify ran into an issue. Make sure Spotify is open and try again.", signals=signals)


def handle_spotify_pause(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    sp = ctx["integrations"]["spotify"]
    if sp.pause():
        speaker.speak("Paused.", signals=signals)
    else:
        speaker.speak("Couldn't pause Spotify. Make sure it's open.", signals=signals)


def handle_spotify_resume(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    sp = ctx["integrations"]["spotify"]
    if sp.resume():
        speaker.speak("Resuming.", signals=signals)
    else:
        speaker.speak("Couldn't resume Spotify.", signals=signals)


def handle_spotify_next(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    sp = ctx["integrations"]["spotify"]
    if sp.next_track():
        speaker.speak("Skipping.", signals=signals)
    else:
        speaker.speak("Couldn't skip the track.", signals=signals)


def handle_spotify_prev(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    sp = ctx["integrations"]["spotify"]
    if sp.prev_track():
        speaker.speak("Going back.", signals=signals)
    else:
        speaker.speak("Couldn't go back.", signals=signals)


def handle_spotify_current(ctx):
    speaker = ctx["speaker"]; signals = ctx["signals"]
    sp = ctx["integrations"]["spotify"]
    if not sp.is_configured:
        speaker.speak("Spotify isn't configured.", signals=signals)
        return
    track = sp.current_track()
    if track:
        speaker.speak(f"Currently playing {track}.", signals=signals)
    else:
        speaker.speak("Nothing is playing on Spotify right now.", signals=signals)


def handle_notion_search(ctx, entities, user_text):
    import webbrowser as _wb
    speaker = ctx["speaker"]; signals = ctx["signals"]; stt = ctx["stt"]
    notion = ctx["integrations"]["notion"]

    if not notion.is_configured:
        speaker.speak("Notion isn't configured. Add NOTION_TOKEN to your .env.", signals=signals)
        return

    query = (entities.get("message_body") or "").strip()
    if not query:
        speaker.speak("What should I search for in Notion?", signals=signals)
        query = listen_for_speech(stt) or ""
    if not query:
        return

    speaker.speak(f"Searching Notion for '{query}'.", signals=signals)
    results = notion.search(query)
    if not results:
        speaker.speak(f"Nothing found in Notion for '{query}'.", signals=signals)
        return

    if len(results) == 1:
        r = results[0]
        speaker.speak(f"Found one page: {r['title']}. Opening it.", signals=signals)
        if r["url"]:
            _wb.open(r["url"])
    else:
        titles = ", ".join(r["title"] for r in results[:3])
        extra  = f" and {len(results) - 3} more" if len(results) > 3 else ""
        speaker.speak(f"Found {len(results)} results: {titles}{extra}. Opening the top one.", signals=signals)
        if results[0]["url"]:
            _wb.open(results[0]["url"])


# ---------------------------------------------------------------------------
# Core voice loop
# ---------------------------------------------------------------------------

def _drain_mic(wake_listener):
    """Flush any audio that accumulated in the PyAudio buffer during TTS playback.
    Without this, buffered audio is processed on the next listen_for_wake_word()
    call and can immediately re-trigger the wake word."""
    try:
        while wake_listener.stream.get_read_available() >= wake_listener.CHUNK:
            wake_listener.stream.read(wake_listener.CHUNK, exception_on_overflow=False)
    except Exception:
        pass


def _do_goodbye(signals, speaker, wake_listener):
    """
    Shared goodbye sequence used by both the wake-word toggle and the 'dismiss' intent.
    speak() is blocking — the audio finishes BEFORE toggle_avatar(False) is emitted,
    so the avatar stays visible while Atlas speaks and disappears immediately after.
    """
    print(">> Going to Sleep...")
    speaker.speak("Goodbye. See you soon.", signals=signals)
    # toggle_avatar is connected to avatar.set_visible (@pyqtSlot) so Qt
    # always dispatches this on the main thread via the event queue.
    signals.toggle_avatar.emit(False)
    wake_listener.model.reset()
    _drain_mic(wake_listener)
    time.sleep(1.0)

def voice_worker(signals, speaker, brain, intent_router, gmail_client, gcal_client,
                 app_launcher, health_tracker, task_store, root_folder, integrations):
    wake_listener = AtlasListener()
    stt = sr.Recognizer()
    stt.dynamic_energy_threshold = True
    stt.pause_threshold = 0.9  # Allows natural mid-sentence pauses without cutting off
    with sr.Microphone() as _src:
        stt.adjust_for_ambient_noise(_src, duration=1.0)
    print(f"[Atlas] Mic calibrated — energy threshold: {stt.energy_threshold:.0f}")
    is_active = False

    pomodoro  = PomodoroTimer()
    focus     = FocusMode()
    reminders = ReminderEngine(speaker, signals)

    ctx = {
        "stt":           stt,
        "signals":       signals,
        "speaker":       speaker,
        "brain":         brain,
        "router":        intent_router,
        "gmail":         gmail_client,
        "gcal":          gcal_client,
        "launcher":      app_launcher,
        "health":        health_tracker,
        "tasks":         task_store,
        "reminders":     reminders,
        "integrations":  integrations,
        "root_folder":   root_folder,
        "email_context": [],
        "active_email":  None,
    }

    passive_start, passive_stop = _make_passive_listener(speaker, signals)
    emotional_mode = False
    resume_text = None  # Text being spoken when last interrupted via "stop"

    _GO_ON_PHRASES = ("go on", "proceed", "continue", "resume", "go ahead", "keep going")

    print("--- Atlas Online: Ready ---")

    while True:
        word = wake_listener.listen_for_wake_word()

        if word == "alexa":
            if not is_active:
                print(">> Waking Up...")
                signals.toggle_avatar.emit(True)
                is_active = True
                speaker.speak("Here.", signals=signals)
                wake_listener.model.reset()
                _drain_mic(wake_listener)
            else:
                _do_goodbye(signals, speaker, wake_listener)
                is_active = False
                continue

        if is_active:
            try:
                user_text = listen_for_speech(stt)
                if not user_text:
                    continue

                print(f"You: {user_text}")

                # Resume previously interrupted speech if user asks to continue
                _low = user_text.lower().strip()
                if resume_text and any(p in _low for p in _GO_ON_PHRASES):
                    speaker.speak(f"As I was saying, {resume_text}", signals=signals)
                    resume_text = None
                    continue

                intent_data = intent_router.classify(user_text)
                intent = intent_data.get("intent", "general_chat")
                entities = intent_data.get("entities", {})

                if intent == "dismiss":
                    passive_stop()
                    _do_goodbye(signals, speaker, wake_listener)
                    is_active = False
                    emotional_mode = False

                elif intent == "close_dashboard":
                    passive_stop()
                    dashboard_cmd("close")
                    speaker.speak("Dashboard closed.", signals=signals)

                elif intent == "open_dashboard":
                    import webbrowser
                    port = int(os.getenv("DASHBOARD_PORT", 7000))
                    webbrowser.open(f"http://127.0.0.1:{port}/world")
                    speaker.speak("Opening your dashboard.", signals=signals)
                    passive_start()

                elif intent == "daily_summary":
                    handle_daily_summary(ctx)

                elif intent == "email_summary":
                    handle_email_summary(ctx)

                elif intent == "schedule_event":
                    handle_schedule(ctx, entities, ctx.get("active_email"))

                elif intent == "send_email":
                    handle_send_email(ctx, entities, user_text)

                elif intent == "draft_reply":
                    active = ctx.get("active_email") or (ctx["email_context"][0] if ctx["email_context"] else None)
                    if active:
                        handle_draft_reply(ctx, entities, active)
                    else:
                        speaker.speak("I don't have an active email to reply to. Ask for email summaries first.", signals=signals)

                elif intent == "log_health":
                    handle_log_health(ctx, user_text)
                    clear_dashboard_cache("health")
                    dashboard_cmd("refresh:health")

                elif intent == "health_summary":
                    handle_health_summary(ctx)

                elif intent == "health_advice":
                    handle_health_advice(ctx)

                elif intent == "open_app":
                    handle_open_app(ctx, entities)

                elif intent == "close_app":
                    handle_close_app(ctx, entities)

                elif intent == "type_text":
                    handle_type_text(ctx, entities)

                # ── Productivity ──────────────────────────────────
                elif intent == "add_task":
                    emotional_mode = False
                    handle_add_task(ctx, entities, user_text)
                    dashboard_cmd("refresh:tasks")

                elif intent == "complete_task":
                    emotional_mode = False
                    handle_complete_task(ctx, entities)
                    dashboard_cmd("refresh:tasks")

                elif intent == "list_tasks":
                    emotional_mode = False
                    handle_list_tasks(ctx)

                elif intent == "delete_task":
                    emotional_mode = False
                    handle_delete_task(ctx, entities)
                    dashboard_cmd("refresh:tasks")

                elif intent == "start_timer":
                    emotional_mode = False
                    handle_start_timer(ctx, entities, pomodoro)

                elif intent == "stop_timer":
                    handle_stop_timer(ctx, pomodoro)

                elif intent == "timer_status":
                    handle_timer_status(ctx, pomodoro)

                elif intent == "start_focus_mode":
                    emotional_mode = False
                    handle_start_focus(ctx, entities, focus)

                elif intent == "end_focus_mode":
                    handle_end_focus(ctx, focus)

                elif intent == "clipboard_summarise":
                    handle_clipboard_summarise(ctx)

                elif intent == "clipboard_improve":
                    handle_clipboard_improve(ctx, entities)

                # ── Information on demand ─────────────────────────
                elif intent == "calculate":
                    handle_calculate(ctx, entities, user_text)

                elif intent == "convert_units":
                    handle_convert(ctx, entities, user_text)

                elif intent == "get_weather":
                    handle_weather(ctx, entities, user_text)

                elif intent == "web_search":
                    handle_web_search(ctx, entities, user_text)

                elif intent == "define_word":
                    handle_define(ctx, entities, user_text)

                # ── Health reminders ──────────────────────────────
                elif intent == "set_reminder":
                    handle_set_reminder(ctx, entities, reminders)

                elif intent == "stop_reminder":
                    handle_stop_reminder(ctx, entities, user_text, reminders)

                elif intent == "list_reminders":
                    handle_list_reminders(ctx, reminders)

                # ── Media & system control ────────────────────────
                elif intent == "media_play_pause":
                    handle_media_play_pause(ctx)

                elif intent == "media_next":
                    handle_media_next(ctx)

                elif intent == "media_prev":
                    handle_media_prev(ctx)

                elif intent == "volume_up":
                    handle_volume_up(ctx)

                elif intent == "volume_down":
                    handle_volume_down(ctx)

                elif intent == "volume_mute":
                    handle_volume_mute(ctx)

                elif intent == "volume_set":
                    handle_volume_set(ctx, entities, user_text)

                elif intent == "screen_lock":
                    handle_screen_lock(ctx)

                elif intent == "system_shutdown":
                    handle_system_shutdown(ctx)

                elif intent == "system_restart":
                    handle_system_restart(ctx)

                # ── Third-party integrations ──────────────────────
                elif intent == "whatsapp_send":
                    handle_whatsapp_send(ctx, entities, user_text)

                elif intent == "drive_search":
                    handle_drive_search(ctx, entities, user_text)

                elif intent == "github_prs":
                    handle_github_prs(ctx)

                elif intent == "github_issues":
                    handle_github_issues(ctx)

                elif intent == "github_create_issue":
                    handle_github_create_issue(ctx, entities, user_text)

                elif intent == "notion_add_note":
                    handle_notion_add_note(ctx, entities, user_text)

                elif intent == "notion_search":
                    handle_notion_search(ctx, entities, user_text)

                # ── Spotify ───────────────────────────────────────
                elif intent == "spotify_play":
                    handle_spotify_play(ctx, entities, user_text)

                elif intent == "spotify_pause":
                    handle_spotify_pause(ctx)

                elif intent == "spotify_resume":
                    handle_spotify_resume(ctx)

                elif intent == "spotify_next":
                    handle_spotify_next(ctx)

                elif intent == "spotify_prev":
                    handle_spotify_prev(ctx)

                elif intent == "spotify_current":
                    handle_spotify_current(ctx)

                elif intent == "emotional_support":
                    emotional_mode = True
                    handle_emotional_support(ctx, user_text)

                else:
                    if emotional_mode:
                        # Continue the emotional support thread until a task intent breaks it
                        handle_emotional_support(ctx, user_text)
                    else:
                        ai_response = brain.think(user_text)
                        print(f"Atlas: {ai_response}")
                        speaker.speak(ai_response, signals=signals)
                        wake_listener.model.reset()

            except AtlasInterrupted:
                # User said "stop" mid-speech — save context and wait for next command
                _rt = speaker.resume_text or ""
                resume_text = _rt if len(_rt) > 30 else None
                print(f"[Atlas] Interrupted — {'resume stored' if resume_text else 'no resume (short text)'}")
                speaker.speak("Sure, go ahead.", signals=signals, interruptible=False)

            except Exception as e:
                print(f"Voice worker error: {e}")

        time.sleep(0.01)


def start_hotkey(signals):
    def on_activate():
        print(">> Hotkey Detected: Opening Settings...")
        signals.show_settings.emit()

    with keyboard.GlobalHotKeys({'<ctrl>+<shift>+a': on_activate}) as h:
        h.join()


if __name__ == "__main__":
    _instance_lock = _acquire_instance_lock()  # exits if another Atlas is already running

    app = QApplication(sys.argv)

    root_folder = os.path.dirname(os.path.abspath(__file__))

    signals = AtlasSignals()
    avatar = AtlasAvatar(root_folder)  # starts hidden (enforced in initUI)

    speaker = AtlasSpeaker()
    brain = AtlasBrain()
    intent_router = IntentRouter()
    gmail_client = GmailClient()
    gcal_client = GoogleCalendarClient(root_folder)
    app_launcher = AppLauncher()
    health_tracker = HealthTracker(os.path.join(root_folder, "data", "health.db"))
    settings_window = AtlasControlPanel(root_folder)

    def _on_watch_sync(entry):
        parts = [k for k in ("steps", "heart_rate_avg", "spo2", "calories_burned") if entry.get(k)]
        print(f"[Apple Watch Sync] Auto-logged: {', '.join(parts)}")

    watch_receiver = AppleWatchReceiver(health_tracker, port=int(os.getenv("HEALTH_SYNC_PORT", 5757)), on_sync=_on_watch_sync)
    watch_receiver.start()

    integrations = {
        "drive":    DriveClient(root_folder),
        "whatsapp": WhatsAppClient(os.path.join(root_folder, "data", "contacts.json")),
        "github":   GitHubClient(),
        "notion":   NotionClient(),
        "spotify":  SpotifyClient(root_folder),
    }

    notes_store   = NotesStore(os.path.join(root_folder, "data", "notes.db"))
    task_store    = TaskStore(os.path.join(root_folder, "data", "tasks.db"))
    habit_store   = HabitStore(os.path.join(root_folder, "data", "habits.db"))
    finance_store = FinanceStore(os.path.join(root_folder, "data", "finance.db"))
    journal_store = JournalStore(os.path.join(root_folder, "data", "journal.db"))
    start_dashboard({
        "gmail":   gmail_client,
        "gcal":    gcal_client,
        "health":  health_tracker,
        "notes":   notes_store,
        "tasks":   task_store,
        "habits":  habit_store,
        "finance": finance_store,
        "journal": journal_store,
    }, port=int(os.getenv("DASHBOARD_PORT", 7000)))

    signals.toggle_avatar.connect(avatar.set_visible)   # @pyqtSlot → always runs on main thread
    signals.update_avatar.connect(avatar.update_frame)
    signals.show_settings.connect(settings_window.show)

    def update_atlas_config(char, voice):
        avatar.images = {
            "closed":   os.path.join(root_folder, "assets", "avatars", char, "atlas_transparent.png"),
            "open":     os.path.join(root_folder, "assets", "avatars", char, "atlas_mouth_open.png"),
            "wide":     os.path.join(root_folder, "assets", "avatars", char, "atlas_mouth_wide_open.png"),
            "gesture":  os.path.join(root_folder, "assets", "avatars", char, "atlas_hand_gesture.png"),
        }
        speaker.model = os.path.join(root_folder, "assets", "voice_models", voice)
        avatar.update_frame("closed")
        print(f"Configuration Updated: {char} character, {voice} voice.")

    settings_window.settings_changed.connect(update_atlas_config)

    # ── Meeting prep watcher — speaks 5 min before any meeting ──
    def _meeting_prep_watcher():
        from datetime import datetime, timezone
        alerted = set()
        while True:
            try:
                events = gcal_client.get_today_events()
                now = datetime.now(timezone.utc)
                for ev in events:
                    start_str = ev.get("start") or ev.get("start_label", "")
                    ev_id = ev.get("id") or ev.get("title", "")
                    if not start_str or ev_id in alerted:
                        continue
                    try:
                        start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    except Exception:
                        continue
                    mins_until = (start_dt - now).total_seconds() / 60
                    if 4.5 <= mins_until <= 5.5:
                        alerted.add(ev_id)
                        title = ev.get("title", "a meeting")
                        speaker.speak(
                            f"Heads up — {title} starts in 5 minutes.",
                            signals=signals,
                        )
            except Exception:
                pass
            time.sleep(60)

    threading.Thread(target=_meeting_prep_watcher, daemon=True).start()

    threading.Thread(
        target=voice_worker,
        args=(signals, speaker, brain, intent_router, gmail_client, gcal_client,
              app_launcher, health_tracker, task_store, root_folder, integrations),
        daemon=True
    ).start()
    threading.Thread(target=start_hotkey, args=(signals,), daemon=True).start()

    sys.exit(app.exec())