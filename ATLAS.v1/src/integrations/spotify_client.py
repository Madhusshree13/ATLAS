"""
spotify_client.py — Spotify Web API integration.

Supports: play specific song/artist/playlist, pause, resume, skip, previous,
          what's currently playing.

Setup:
  1. Go to https://developer.spotify.com/dashboard → Create App
  2. Set Redirect URI to: http://localhost:8765/callback
  3. Copy Client ID and Client Secret → add to .env

Required env vars:
  SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET

Requires Spotify Premium for playback control.
First use opens a browser login window — sign in once, token auto-refreshes forever.
"""

import os
import json
import time
import base64
import secrets
import threading
import webbrowser
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, parse_qs, urlparse

_AUTH_URL   = "https://accounts.spotify.com/authorize"
_TOKEN_URL  = "https://accounts.spotify.com/api/token"
_API_BASE   = "https://api.spotify.com/v1"
_REDIRECT   = "http://127.0.0.1:8765/callback"
_SCOPES     = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing"
)
_PORT = 8765


class SpotifyClient:
    def __init__(self, root_folder: str):
        self._client_id     = os.getenv("SPOTIFY_CLIENT_ID",     "").strip()
        self._client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
        self._token_file    = os.path.join(root_folder, "data", "spotify_token.json")
        self._access_token  = None
        self._refresh_token = None
        self._expires_at    = 0
        self._load_tokens()

    @property
    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    # ── Token management ───────────────────────────────────────────────────

    def _load_tokens(self):
        try:
            if os.path.exists(self._token_file):
                with open(self._token_file) as f:
                    d = json.load(f)
                self._access_token  = d.get("access_token")
                self._refresh_token = d.get("refresh_token")
                self._expires_at    = d.get("expires_at", 0)
        except Exception:
            pass

    def _save_tokens(self):
        os.makedirs(os.path.dirname(self._token_file), exist_ok=True)
        with open(self._token_file, "w") as f:
            json.dump({
                "access_token":  self._access_token,
                "refresh_token": self._refresh_token,
                "expires_at":    self._expires_at,
            }, f)

    def _ensure_token(self) -> bool:
        if not self.is_configured:
            return False
        if self._access_token and time.time() < self._expires_at - 30:
            return True
        if self._refresh_token:
            return self._do_refresh()
        return self._do_authorize()

    def _credentials_header(self) -> dict:
        encoded = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()
        return {"Authorization": f"Basic {encoded}"}

    def _do_refresh(self) -> bool:
        try:
            r = requests.post(
                _TOKEN_URL,
                data={"grant_type": "refresh_token", "refresh_token": self._refresh_token},
                headers=self._credentials_header(),
                timeout=8,
            )
            r.raise_for_status()
            d = r.json()
            self._access_token = d["access_token"]
            self._expires_at   = time.time() + d.get("expires_in", 3600)
            if "refresh_token" in d:
                self._refresh_token = d["refresh_token"]
            self._save_tokens()
            return True
        except Exception as e:
            print(f"[Spotify] token refresh error: {e}")
            return False

    def _do_authorize(self) -> bool:
        """One-time browser OAuth. Opens browser, waits up to 2 minutes for callback."""
        auth_url = (
            _AUTH_URL + "?" + urlencode({
                "client_id":     self._client_id,
                "response_type": "code",
                "redirect_uri":  _REDIRECT,
                "scope":         _SCOPES,
                "state":         secrets.token_urlsafe(12),
            })
        )

        code_holder = [None]
        done        = threading.Event()

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                qs = parse_qs(urlparse(self.path).query)
                if "code" in qs:
                    code_holder[0] = qs["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h2 style='font-family:sans-serif;margin:60px auto;text-align:center'>"
                    b"Atlas connected to Spotify! You can close this tab.</h2>"
                )
                done.set()

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", _PORT), _Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()

        print("[Spotify] Opening browser for one-time login...")
        webbrowser.open(auth_url)
        done.wait(timeout=120)
        server.shutdown()

        if not code_holder[0]:
            print("[Spotify] Auth timed out — no code received.")
            return False
        return self._exchange_code(code_holder[0])

    def _exchange_code(self, code: str) -> bool:
        try:
            r = requests.post(
                _TOKEN_URL,
                data={
                    "grant_type":   "authorization_code",
                    "code":         code,
                    "redirect_uri": _REDIRECT,
                },
                headers=self._credentials_header(),
                timeout=8,
            )
            r.raise_for_status()
            d = r.json()
            self._access_token  = d["access_token"]
            self._refresh_token = d.get("refresh_token", "")
            self._expires_at    = time.time() + d.get("expires_in", 3600)
            self._save_tokens()
            print("[Spotify] Authorized and token saved.")
            return True
        except Exception as e:
            print(f"[Spotify] code exchange error: {e}")
            return False

    # ── Playback API ───────────────────────────────────────────────────────

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._access_token}"}

    def search_and_play(self, query: str) -> tuple:
        """
        Search Spotify for the query (song, artist, album, playlist, genre)
        and immediately start playing the best match.
        Returns (success: bool, display_name: str).
        """
        if not self._ensure_token():
            return False, "not_configured"

        try:
            r = requests.get(
                f"{_API_BASE}/search",
                params={"q": query, "type": "track,playlist,album", "limit": 1},
                headers=self._headers(),
                timeout=8,
            )
            r.raise_for_status()
            data = r.json()

            # Prefer track → album → playlist
            tracks = data.get("tracks", {}).get("items", [])
            albums = data.get("albums", {}).get("items", [])
            playlists = data.get("playlists", {}).get("items", [])

            if tracks:
                track = tracks[0]
                name  = f"{track['name']} by {track['artists'][0]['name']}"
                play_kwargs = {"uris": [track["uri"]]}
            elif albums:
                album = albums[0]
                name  = f"album: {album['name']}"
                play_kwargs = {"context_uri": album["uri"]}
            elif playlists:
                pl   = playlists[0]
                name = f"playlist: {pl['name']}"
                play_kwargs = {"context_uri": pl["uri"]}
            else:
                return False, "nothing_found"

            ok, reason = self._start_playback(**play_kwargs)
            if ok:
                return True, name
            return False, reason

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 403:
                return False, "premium_required"
            print(f"[Spotify] search error: {e}")
            return False, "error"
        except Exception as e:
            print(f"[Spotify] search error: {e}")
            return False, "error"

    def _start_playback(self, uris: list = None, context_uri: str = None) -> tuple:
        """Send play command. Returns (True, '') on success or (False, reason) on failure."""
        body = {}
        if uris:
            body["uris"] = uris
        elif context_uri:
            body["context_uri"] = context_uri
        try:
            r = requests.put(
                f"{_API_BASE}/me/player/play",
                json=body,
                headers=self._headers(),
                timeout=8,
            )
            if r.status_code == 204:
                return True, ""
            if r.status_code == 403:
                return False, "premium_required"
            if r.status_code == 404:
                return False, "no_device"
            if r.status_code == 401:
                return False, "not_configured"
            r.raise_for_status()
            return True, ""
        except requests.exceptions.HTTPError as e:
            print(f"[Spotify] playback error: {e}")
            return False, "error"
        except Exception as e:
            print(f"[Spotify] playback error: {e}")
            return False, "error"

    def pause(self) -> bool:
        if not self._ensure_token():
            return False
        try:
            requests.put(f"{_API_BASE}/me/player/pause",
                         headers=self._headers(), timeout=8)
            return True
        except Exception:
            return False

    def resume(self) -> bool:
        if not self._ensure_token():
            return False
        try:
            requests.put(f"{_API_BASE}/me/player/play",
                         headers=self._headers(), timeout=8)
            return True
        except Exception:
            return False

    def next_track(self) -> bool:
        if not self._ensure_token():
            return False
        try:
            requests.post(f"{_API_BASE}/me/player/next",
                          headers=self._headers(), timeout=8)
            return True
        except Exception:
            return False

    def prev_track(self) -> bool:
        if not self._ensure_token():
            return False
        try:
            requests.post(f"{_API_BASE}/me/player/previous",
                          headers=self._headers(), timeout=8)
            return True
        except Exception:
            return False

    def current_track(self) -> str:
        """Return 'Song by Artist' for the currently playing track, or empty string."""
        if not self._ensure_token():
            return ""
        try:
            r = requests.get(f"{_API_BASE}/me/player/currently-playing",
                             headers=self._headers(), timeout=8)
            if r.status_code == 204:
                return ""
            item = r.json().get("item") or {}
            if not item:
                return ""
            artists = ", ".join(a["name"] for a in item.get("artists", []))
            return f"{item['name']} by {artists}"
        except Exception:
            return ""
