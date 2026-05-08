"""
drive_client.py — Google Drive search via the Drive v3 API.
Reuses the same credentials.json as Calendar but keeps a
separate token file (assets/drive_token.json).
"""

import os
import webbrowser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class DriveClient:
    def __init__(self, root_folder: str):
        self._root       = root_folder
        self._creds_file = os.path.join(root_folder, "assets", "credentials.json")
        self._token_file = os.path.join(root_folder, "assets", "drive_token.json")
        self._service    = None
        # Attempt silent auth only (no browser). Browser OAuth deferred to first use.
        self._try_silent_auth()

    def _try_silent_auth(self):
        """Load existing token and refresh if expired. Never opens a browser."""
        if not os.path.exists(self._creds_file) or not os.path.exists(self._token_file):
            return
        try:
            from google.oauth2.credentials import Credentials

            creds = Credentials.from_authorized_user_file(self._token_file, _SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(self._token_file, "w") as f:
                    f.write(creds.to_json())
            if creds and creds.valid:
                self._service = build("drive", "v3", credentials=creds)
                print("[Drive] Connected (token loaded).")
        except Exception as e:
            print(f"[Drive] Silent auth failed: {e}")

    def _ensure_service(self) -> bool:
        """Connect if not already connected. Runs browser OAuth on first use."""
        if self._service:
            return True
        if not os.path.exists(self._creds_file):
            print("[Drive] credentials.json not found — cannot authenticate.")
            return False
        try:
            from google.oauth2.credentials import Credentials

            creds = None
            if os.path.exists(self._token_file):
                creds = Credentials.from_authorized_user_file(self._token_file, _SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    print("[Drive] Opening browser for one-time Google sign-in...")
                    flow = InstalledAppFlow.from_client_secrets_file(self._creds_file, _SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(self._token_file, "w") as f:
                    f.write(creds.to_json())

            self._service = build("drive", "v3", credentials=creds)
            print("[Drive] Connected.")
            return True
        except Exception as e:
            print(f"[Drive] Auth error: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        return self._service is not None

    def search(self, query: str, max_results: int = 5) -> list:
        """Search Drive files by name. Returns list of {name, link, modified}."""
        if not self._ensure_service():
            return []
        try:
            safe = query.replace("'", "\\'")
            q = f"name contains '{safe}' and trashed = false"
            resp = self._service.files().list(
                q=q,
                pageSize=max_results,
                orderBy="modifiedTime desc",
                fields="files(id,name,mimeType,modifiedTime,webViewLink)",
            ).execute()
            return [
                {
                    "name":     f["name"],
                    "link":     f.get("webViewLink", ""),
                    "modified": f.get("modifiedTime", "")[:10],
                }
                for f in resp.get("files", [])
            ]
        except Exception as e:
            print(f"[Drive] search error: {e}")
            return []

    def open_file(self, link: str):
        if link:
            webbrowser.open(link)
