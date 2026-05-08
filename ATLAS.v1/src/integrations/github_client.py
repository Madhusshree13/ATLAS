"""
github_client.py — GitHub REST API integration.

Required env vars:
  GITHUB_TOKEN       — Personal Access Token (repo + read:user scopes)
  GITHUB_USERNAME    — Your GitHub username
  GITHUB_DEFAULT_REPO — "owner/repo" used when creating issues (optional)

Token creation: https://github.com/settings/tokens
"""

import os
import webbrowser
import requests


class GitHubClient:
    _BASE = "https://api.github.com"

    def __init__(self):
        self._token    = os.getenv("GITHUB_TOKEN", "").strip()
        self._username = os.getenv("GITHUB_USERNAME", "").strip()
        self._repo     = os.getenv("GITHUB_DEFAULT_REPO", "").strip()
        self._headers  = {
            "Authorization": f"Bearer {self._token}",
            "Accept":        "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @property
    def is_configured(self) -> bool:
        return bool(self._token and self._username)

    def _get(self, path: str, params: dict = None) -> dict:
        try:
            r = requests.get(
                f"{self._BASE}{path}",
                params=params,
                headers=self._headers,
                timeout=8,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[GitHub] GET {path} error: {e}")
            return {}

    def my_open_prs(self, limit: int = 5) -> list:
        """Return open PRs authored by the configured user."""
        data = self._get(
            "/search/issues",
            {"q": f"type:pr state:open author:{self._username}", "per_page": limit},
        )
        items = data.get("items", []) if isinstance(data, dict) else []
        return [
            {
                "title": i["title"],
                "repo":  "/".join(i.get("repository_url", "").split("/")[-2:]),
                "url":   i.get("html_url", ""),
            }
            for i in items
        ]

    def my_open_issues(self, limit: int = 5) -> list:
        """Return open issues assigned to the configured user."""
        data = self._get("/issues", {"state": "open", "per_page": limit})
        if not isinstance(data, list):
            return []
        return [
            {
                "title": i["title"],
                "repo":  i.get("repository", {}).get("name", "?"),
                "url":   i.get("html_url", ""),
            }
            for i in data
        ]

    def create_issue(self, title: str, body: str = "", repo: str = "") -> str:
        """Create an issue. Returns issue URL or empty string."""
        target = repo or self._repo
        if not target:
            return ""
        try:
            owner, repo_name = target.split("/", 1)
            r = requests.post(
                f"{self._BASE}/repos/{owner}/{repo_name}/issues",
                json={"title": title, "body": body},
                headers=self._headers,
                timeout=8,
            )
            r.raise_for_status()
            return r.json().get("html_url", "")
        except Exception as e:
            print(f"[GitHub] create_issue error: {e}")
            return ""

    def open_in_browser(self, url: str):
        if url:
            webbrowser.open(url)
