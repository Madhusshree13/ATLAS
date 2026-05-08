"""
notion_client.py — Notion API integration (search + quick note creation).

Required env vars:
  NOTION_TOKEN           — Internal integration secret
  NOTION_DEFAULT_PAGE_ID — Page ID where new notes are created as sub-pages

Setup:
  1. Go to https://www.notion.so/my-integrations → New integration
  2. Copy the "Internal Integration Secret" → NOTION_TOKEN
  3. Open the Notion page you want notes under → Share → Add your integration
  4. Copy the page ID from the URL (32-char hex after last /) → NOTION_DEFAULT_PAGE_ID
"""

import os
import webbrowser
import requests
from datetime import datetime


class NotionClient:
    _API = "https://api.notion.com/v1"
    _VER = "2022-06-28"

    def __init__(self):
        self._token   = os.getenv("NOTION_TOKEN", "").strip()
        self._page_id = os.getenv("NOTION_DEFAULT_PAGE_ID", "").strip()
        self._headers = {
            "Authorization":  f"Bearer {self._token}",
            "Content-Type":   "application/json",
            "Notion-Version": self._VER,
        }

    @property
    def is_configured(self) -> bool:
        return bool(self._token)

    def search(self, query: str, limit: int = 5) -> list:
        """Search all pages/databases the integration can access."""
        if not self.is_configured:
            return []
        try:
            r = requests.post(
                f"{self._API}/search",
                json={"query": query, "page_size": limit},
                headers=self._headers,
                timeout=8,
            )
            r.raise_for_status()
            out = []
            for item in r.json().get("results", []):
                title = self._extract_title(item)
                out.append({
                    "title": title or "Untitled",
                    "url":   item.get("url", ""),
                    "type":  item.get("object", "page"),
                })
            return out
        except Exception as e:
            print(f"[Notion] search error: {e}")
            return []

    def add_note(self, title: str, content: str) -> bool:
        """Create a new child page under NOTION_DEFAULT_PAGE_ID."""
        if not self.is_configured or not self._page_id:
            return False
        note_title = title or f"Voice Note — {datetime.now():%b %d, %Y %H:%M}"
        payload = {
            "parent": {"page_id": self._page_id},
            "properties": {
                "title": {
                    "title": [{"type": "text", "text": {"content": note_title}}]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type":   "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    },
                }
            ],
        }
        try:
            r = requests.post(
                f"{self._API}/pages",
                json=payload,
                headers=self._headers,
                timeout=8,
            )
            r.raise_for_status()
            url = r.json().get("url", "")
            if url:
                webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[Notion] add_note error: {e}")
            return False

    def _extract_title(self, item: dict) -> str:
        props = item.get("properties", {})
        for v in props.values():
            if v.get("type") == "title":
                return "".join(t.get("plain_text", "") for t in v.get("title", []))
        return ""
