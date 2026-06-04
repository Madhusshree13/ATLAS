## ✨ What is Atlas?

Atlas is a fully local, privacy-first voice assistant that lives on your desktop as an animated avatar. Say the wake word, give a command, and Atlas handles everything — searching Spotify, reading your emails, scheduling meetings, logging your health, managing tasks, and much more.

Unlike cloud assistants, Atlas processes your commands through Groq's ultra-fast inference API and keeps your personal data on your own machine.

---


<div align="center">

# 🌐 ATLAS

### *Your Personal AI Voice Assistant*

A voice-driven AI assistant with a live avatar overlay, natural language understanding, and deep integration with your digital life — email, calendar, Spotify, tasks, health, and more.

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-Dashboard-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

</div>

---

## ✨ What is Atlas?

Atlas is a fully local, privacy-first voice assistant that lives on your desktop as an animated avatar. Say the wake word, give a command, and Atlas handles everything — searching Spotify, reading your emails, scheduling meetings, logging your health, managing tasks, and much more.

Unlike cloud assistants, Atlas processes your commands through Groq's ultra-fast inference API and keeps your personal data on your own machine.

---

## 🎬 Features at a Glance

| Category | Capabilities |
|----------|-------------|
| 🎙️ **Voice** | Wake word detection · Speech-to-text · Piper TTS with lip-sync avatar |
| 🧠 **AI Brain** | Groq LLM (Llama 3) · Intent routing · Natural conversation · Emotional support mode |
| 🎵 **Spotify** | Search & play songs/albums/playlists · Pause · Skip · Volume control |
| 📧 **Gmail** | Read today's emails · Compose & send · Reply to threads |
| 📅 **Calendar** | Schedule events · Conflict detection · Smart slot finder · Meeting reminders |
| 📂 **Google Drive** | Search files · Open in browser |
| ✅ **Tasks** | Add · Complete · Delete · List pending — syncs live to dashboard |
| 💪 **Health** | Log steps, water, sleep, heart rate · 7-day analytics · Pattern detection |
| 🔄 **Habits** | Daily habit tracking · 30-day history grid · Streak counters |
| 📓 **Journal** | Daily entries · Mood tracking · Full-text search |
| 📝 **Notes** | Create & edit sticky notes · Color-coded · Persistent |
| 🎨 **Whiteboard** | Multi-board canvas · Draw · Text · Sticky notes · Undo |
| 💰 **Finance** | Income & expense tracking · Category breakdown · Monthly summary |
| ⏱️ **Productivity** | Pomodoro timer · Focus mode · Smart reminders |
| 🖥️ **System** | App launcher · Media control · Volume · Screen lock · Shutdown |
| 💬 **Integrations** | GitHub · Notion · WhatsApp · Web search |
| 🛑 **Interrupt** | Say *"stop"* to pause Atlas mid-speech · Say *"go on"* to resume |

---

## 🗂️ Project Structure

```
ATLAS.v1/
├── main.py                     # Core voice worker, intent dispatch, all handlers
├── requirements.txt
├── run.bat                     # Windows launcher
│
├── assets/
│   └── avatars/                # Avatar images (closed, open, wide, gesture)
│       └── default/
│
└── src/
    ├── voice/
    │   ├── listener.py         # Wake word detection (openwakeword)
    │   └── speaker.py          # Piper TTS + lip-sync + interrupt detection
    │
    ├── brain/
    │   ├── llm_client.py       # Groq LLM — conversation, health, email drafting
    │   └── intent_router.py    # 72-intent classifier (llama-3.1-8b-instant)
    │
    ├── integrations/
    │   ├── spotify_client.py   # Spotify Web API — OAuth, search, playback
    │   ├── drive_client.py     # Google Drive — search, open
    │   ├── github_client.py    # GitHub — PRs, issues
    │   ├── notion_client.py    # Notion — notes, search
    │   └── whatsapp_client.py  # WhatsApp messaging
    │
    ├── email/
    │   └── gmail_client.py     # Gmail IMAP/SMTP
    │
    ├── calendar/
    │   └── gcal_client.py      # Google Calendar — events, conflicts, free slots
    │
    ├── dashboard/
    │   ├── server.py           # Flask backend + SSE live updates
    │   ├── notes_store.py      # SQLite notes & whiteboards
    │   ├── habit_store.py      # SQLite habit logs
    │   ├── journal_store.py    # SQLite journal entries
    │   ├── finance_store.py    # SQLite transactions
    │   ├── templates/
    │   │   └── world.html      # Dashboard UI
    │   └── static/js/          # habits.js, journal.js, whiteboard.js, …
    │
    ├── productivity/
    │   ├── task_store.py       # SQLite task management
    │   ├── pomodoro.py         # Focus timer
    │   ├── focus_mode.py       # Distraction blocking
    │   └── reminder_engine.py  # Interval reminders
    │
    ├── health/
    │   └── health_tracker.py   # SQLite health metrics + analytics
    │
    ├── apps/
    │   └── app_launcher.py     # Launch/close apps by voice (Win registry + UWP)
    │
    ├── system/
    │   └── media_control.py    # Media keys, volume
    │
    ├── gui/
    │   ├── overlay.py          # Qt6 avatar widget (always-on-top, draggable)
    │   └── settings.py         # Character & voice selector panel
    │
    └── info/
        └── tools.py            # Weather, definitions
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Windows 10/11** (primary target; macOS/Linux partially supported)
- **Microphone** connected
- **[Piper TTS](https://github.com/rhasspy/piper/releases)** — download the Windows binary and place it at:
  ```
  assets/piper_windows_amd64/piper/piper.exe
  assets/piper_windows_amd64/piper/en_US-lessac-medium.onnx
  ```

### 1. Clone & install

```bash
git clone https://github.com/Madhusshree13/ATLAS.git
cd ATLAS/ATLAS.v1
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Configure `.env`

Create a `.env` file in `ATLAS.v1/` (copy the template below):

```env
# ── AI ────────────────────────────────────────────────────
GROQ_API_KEY=your_groq_api_key_here

# ── Gmail (IMAP/SMTP) ─────────────────────────────────────
# Requires 2-Step Verification + App Password from myaccount.google.com/apppasswords
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx

# ── Google Calendar + Drive (OAuth) ───────────────────────
# 1. console.cloud.google.com → New Project
# 2. Enable: Google Calendar API + Google Drive API
# 3. Credentials → OAuth 2.0 Client ID → Desktop App → Download JSON
# 4. Rename to credentials.json → place in assets/
TIMEZONE=Asia/Kolkata

# ── Spotify ───────────────────────────────────────────────
# developer.spotify.com/dashboard → Create App → Redirect URI: http://127.0.0.1:8765/callback
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# ── GitHub ────────────────────────────────────────────────
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=YourUsername
GITHUB_DEFAULT_REPO=YourUsername/YourRepo

# ── Notion ────────────────────────────────────────────────
NOTION_TOKEN=secret_your_token
NOTION_DEFAULT_PAGE_ID=your_page_id

# ── Misc ──────────────────────────────────────────────────
DEFAULT_CITY=Bangalore
DASHBOARD_PORT=7000
```

### 3. Run

```bash
python main.py
```

> On first run, Atlas will open browser tabs for Google Calendar and Drive authorization — complete the sign-in once, and tokens are cached forever.

---

## 🗣️ Voice Commands

Say the wake word **"Alexa"** to wake Atlas, then speak your command.

| What you say | What Atlas does |
|---|---|
| *"Play Blinding Lights on Spotify"* | Searches Spotify and starts playback |
| *"Pause Spotify"* / *"Skip this"* | Pauses / skips the current track |
| *"Read my emails"* | Fetches and narrates today's inbox |
| *"Send an email to Madhu saying the meeting is rescheduled"* | Drafts, reads back, and sends on confirmation |
| *"Schedule a meeting with Priya tomorrow at 3 PM"* | Creates calendar event with conflict detection |
| *"Add task: finish the report by Friday"* | Adds to task list, syncs to dashboard |
| *"I walked 8000 steps and drank 2 litres of water"* | Logs health data |
| *"Search Drive for the project presentation"* | Finds file and opens in browser |
| *"Open Gmail"* | Opens Gmail in the default browser |
| *"Start a 25-minute focus session"* | Starts Pomodoro timer |
| *"What's the weather in Bangalore?"* | Reports live weather |
| *"Stop"* *(while Atlas is talking)* | Instantly stops TTS |
| *"Go on"* *(after stopping)* | Resumes from where it stopped |
| *"Goodbye"* | Atlas goes back to sleep |

---

## 🌐 Dashboard

Say **"open my dashboard"** or visit `http://127.0.0.1:7000/world`.

The dashboard is a real-time web UI with live SSE updates — when you add a task or schedule a meeting by voice, the dashboard refreshes instantly without a page reload.

| Panel | Description |
|-------|-------------|
| 📧 Email | Today's inbox with sender analytics |
| ✅ Tasks | Pending & completed task list |
| 📅 Meetings | Day timeline + utilization bar |
| 💪 Health | Activity rings + 7-day sparklines |
| 🔄 Habits | Daily checklist + 30-day scroll grid |
| 📆 Calendar | Monthly calendar view |
| 📓 Journal | Daily entries with mood picker |
| 📝 Notes | Sticky notes with colour coding |
| 🎨 Whiteboard | Multi-board Fabric.js canvas |
| 💰 Finance | Income/expense tracker |
| 🖥️ System | Live CPU, RAM, disk, network monitor |

---

## 🏗️ Architecture

```
Wake Word (openwakeword)
        ↓
  Speech-to-Text (Google STT)
        ↓
  Intent Router (Groq llama-3.1-8b-instant)
        ↓
  Handler Dispatch (72 intents)
     ↙        ↘
Integrations   Response
(Spotify, Gmail, (Groq llama-3.3-70b)
 Calendar, …)      ↓
        ↓     Piper TTS
  SQLite DBs   Avatar lip-sync
        ↓
 Flask Dashboard ←── SSE live refresh
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| GUI | PyQt6 · always-on-top transparent avatar |
| Wake word | openwakeword (ONNX Alexa model) |
| Speech-to-text | SpeechRecognition · Google STT API |
| Text-to-speech | Piper TTS (en_US-lessac-medium) |
| LLM | Groq API · Llama 3.1 8B (intent) · Llama 3.3 70B (responses) |
| Dashboard | Flask · Server-Sent Events · Vanilla JS |
| Storage | SQLite (tasks, health, habits, journal, notes, finance) |
| Voice integrations | Spotify Web API · Gmail IMAP/SMTP · Google Calendar/Drive OAuth2 |
| System | pynput · psutil · dateparser |

---

## 🔒 Privacy & Security

- All voice processing happens locally (wake word detection is fully on-device)
- STT uses Google's API over HTTPS — audio is not stored
- LLM calls go to Groq's API — no conversation history is sent, only the current turn
- All personal data (tasks, journal, health, notes) is stored in local SQLite databases
- **Never commit your `.env` file** — it contains API keys and credentials

---

## 📦 What's Not Included

To keep the repo lightweight and secure, the following are excluded:

| Excluded | Why | How to get it |
|----------|-----|---------------|
| `assets/piper_windows_amd64/` | ~200 MB binary | [Piper releases](https://github.com/rhasspy/piper/releases) |
| `.env` | Contains API keys | Create from template above |
| `assets/credentials.json` | OAuth client secret | Google Cloud Console |
| `data/*.db` | Personal user data | Created automatically on first run |
| `venv/` | Python environment | `pip install -r requirements.txt` |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

<div align="center">

Built  by [Madhusshree](https://github.com/Madhusshree13)

</div>
