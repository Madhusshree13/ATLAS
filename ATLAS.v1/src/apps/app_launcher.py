import os
import glob
import subprocess
import difflib
import webbrowser
import psutil

# Common voice aliases → canonical registry key (resolved before fuzzy search)
_ALIASES = {
    "vs code":          "visual studio code",
    "vscode":           "visual studio code",
    "visual studio":    "visual studio code",
    "chrome":           "google chrome",
    "ms word":          "microsoft word",
    "word":             "microsoft word",
    "excel":            "microsoft excel",
    "powerpoint":       "microsoft powerpoint",
    "ppt":              "microsoft powerpoint",
    "ms edge":          "microsoft edge",
    "edge browser":     "microsoft edge",
    "file manager":     "file explorer",
    "files":            "file explorer",
    "notepad plus":     "notepad++",
    "note pad":         "notepad",
    "teams":            "microsoft teams",
    "outlook":          "microsoft outlook",
    "one note":         "microsoft onenote",
    "onenote":          "microsoft onenote",
    "task mgr":         "task manager",
    # Drive / folder aliases
    "c drive":          "c:",
    "local disk":       "c:",
    "local disk c":     "c:",
    "d drive":          "d:",
    "e drive":          "e:",
    "my documents":     "documents",
    "my downloads":     "downloads",
    "my desktop":       "desktop",
    "my pictures":      "pictures",
    "my music":         "music",
    "my videos":        "videos",
    "one drive":        "onedrive",
}

# UWP / Microsoft Store apps — launched via shell:AppsFolder AppUserModelID
# PackageFamilyName is stable across version updates
_UWP_APPS = {
    "whatsapp":  r"shell:AppsFolder\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "spotify":   r"shell:AppsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
    "netflix":   r"shell:AppsFolder\4DF9E0F3.Netflix_mcm4njqhnhss8!Netflix.App",
    "instagram": r"shell:AppsFolder\Facebook.InstagramBeta_8xx8rvfyw5nnt!App",
}

# Web apps — opened in the default browser
_WEB_APPS = {
    "gmail":            "https://mail.google.com",
    "google mail":      "https://mail.google.com",
    "google drive":     "https://drive.google.com",
    "google calendar":  "https://calendar.google.com",
    "google meet":      "https://meet.google.com",
    "google docs":      "https://docs.google.com",
    "google sheets":    "https://sheets.google.com",
    "google slides":    "https://slides.google.com",
    "google":           "https://www.google.com",
    "youtube":          "https://www.youtube.com",
    "github":           "https://github.com",
    "notion":           "https://www.notion.so",
    "chatgpt":          "https://chat.openai.com",
    "linkedin":         "https://www.linkedin.com",
    "twitter":          "https://twitter.com",
    "facebook":         "https://www.facebook.com",
}

# System apps + folder shortcuts
_SYSTEM_APPS = {
    "calculator":       "calc.exe",
    "notepad":          "notepad.exe",
    "command prompt":   "cmd.exe",
    "cmd":              "cmd.exe",
    "terminal":         "wt.exe",
    "windows terminal": "wt.exe",
    "task manager":     "taskmgr.exe",
    "file explorer":    "explorer.exe",
    "file manager":     "explorer.exe",
    "paint":            "mspaint.exe",
    "wordpad":          "wordpad.exe",
    "snipping tool":    "snippingtool.exe",
    "control panel":    "control.exe",
    "settings":         "ms-settings:",
    "registry editor":  "regedit.exe",
    "device manager":   "devmgmt.msc",
    "powershell":       "powershell.exe",
    # Drives
    "c:":               r"C:\\",
    "d:":               r"D:\\",
    "e:":               r"E:\\",
    # Common user folders
    "downloads":        os.path.expandvars(r"%USERPROFILE%\Downloads"),
    "documents":        os.path.expandvars(r"%USERPROFILE%\Documents"),
    "desktop":          os.path.expandvars(r"%USERPROFILE%\Desktop"),
    "pictures":         os.path.expandvars(r"%USERPROFILE%\Pictures"),
    "music":            os.path.expandvars(r"%USERPROFILE%\Music"),
    "videos":           os.path.expandvars(r"%USERPROFILE%\Videos"),
    "onedrive":         os.path.expandvars(r"%USERPROFILE%\OneDrive"),
}

# Maps voice app names to their process executable names (for close)
_PROCESS_MAP = {
    "chrome":               "chrome.exe",
    "google chrome":        "chrome.exe",
    "firefox":              "firefox.exe",
    "edge":                 "msedge.exe",
    "microsoft edge":       "msedge.exe",
    "spotify":              "spotify.exe",
    "discord":              "discord.exe",
    "code":                 "code.exe",
    "vs code":              "code.exe",
    "visual studio code":   "code.exe",
    "notepad":              "notepad.exe",
    "calculator":           "calculator.exe",
    "explorer":             "explorer.exe",
    "file explorer":        "explorer.exe",
    "telegram":             "telegram.exe",
    "whatsapp":             "whatsapp.exe",
    "zoom":                 "zoom.exe",
    "teams":                "teams.exe",
    "microsoft teams":      "teams.exe",
    "vlc":                  "vlc.exe",
    "task manager":         "taskmgr.exe",
    "powershell":           "powershell.exe",
    "terminal":             "windowsterminal.exe",
    "windows terminal":     "windowsterminal.exe",
}


class AppLauncher:
    def __init__(self):
        self.registry = {}   # {normalized_app_name: path_or_exe}
        self._build_registry()

    def _build_registry(self):
        # 1. Seed with known system apps, folders, UWP apps, and web apps
        self.registry.update(_SYSTEM_APPS)
        self.registry.update(_UWP_APPS)
        self.registry.update(_WEB_APPS)

        # 2. Scan Start Menu and Desktop for .lnk shortcuts
        scan_dirs = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.expandvars(r"%USERPROFILE%\Desktop"),
            r"C:\Users\Public\Desktop",
        ]

        lnk_count = 0
        for directory in scan_dirs:
            if not os.path.isdir(directory):
                continue
            for lnk in glob.glob(os.path.join(directory, "**", "*.lnk"), recursive=True):
                name = os.path.splitext(os.path.basename(lnk))[0].lower().strip()
                if any(skip in name for skip in ("uninstall", "setup", "install", "update", "readme")):
                    continue
                if name and name not in self.registry:
                    self.registry[name] = lnk
                    lnk_count += 1

        # 3. Scan WindowsApps (Microsoft Store / UWP apps — Spotify, WhatsApp, etc.)
        windows_apps_dir = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps")
        uwp_count = 0
        if os.path.isdir(windows_apps_dir):
            for exe in glob.glob(os.path.join(windows_apps_dir, "*.exe")):
                name = os.path.splitext(os.path.basename(exe))[0].lower().strip()
                skip_stubs = {"python", "python3", "bash", "wsl", "wslconfig",
                              "winget", "wt", "store", "pwsh"}
                if name in skip_stubs or name in self.registry:
                    continue
                self.registry[name] = exe
                uwp_count += 1

        print(f"AppLauncher: {lnk_count} shortcuts + {len(_SYSTEM_APPS)} system apps + {uwp_count} Store apps indexed.")

    def _fuzzy_find(self, query):
        """Return (matched_name, path) for the best match to query, or (None, None)."""
        query = query.lower().strip()

        # 1. Resolve known aliases first
        query = _ALIASES.get(query, query)

        # 2. Exact match
        if query in self.registry:
            return query, self.registry[query]

        # 3 & 4. Substring / whole-word match
        query_words = set(query.split())
        hits = []
        for name, path in self.registry.items():
            name_words = set(name.split())
            if query_words.issubset(name_words) or query in name:
                hits.append((name, path))
        if hits:
            return min(hits, key=lambda x: len(x[0]))

        # 5. Fuzzy character-level match
        matches = difflib.get_close_matches(query, self.registry.keys(), n=1, cutoff=0.65)
        if matches:
            return matches[0], self.registry[matches[0]]

        return None, None

    def launch(self, app_query):
        """
        Launch an app by voice query.
        Returns (success: bool, matched_name: str | None).
        """
        matched_name, path = self._fuzzy_find(app_query)
        if not path:
            return False, None

        try:
            # Web URLs → open in default browser
            if path.startswith("https://") or path.startswith("http://"):
                webbrowser.open(path)
            # UWP / Store apps via shell:AppsFolder protocol
            elif path.startswith("shell:"):
                subprocess.Popen(["explorer.exe", path])
            # Directory path (drive or folder) → open in File Explorer
            elif os.path.isdir(path):
                subprocess.Popen(['explorer.exe', path])
            elif path.endswith(".lnk") or (not path.endswith(".exe") and ":" not in path):
                os.startfile(path)
            elif path.startswith("ms-"):
                os.startfile(path)
            else:
                subprocess.Popen([path], shell=False)
            return True, matched_name
        except Exception as e:
            print(f"AppLauncher launch error ({path}): {e}")
            return False, matched_name

    def close(self, app_query):
        """
        Terminate a running app by voice query.
        Returns (success: bool, process_name: str | None).
        """
        query = app_query.lower().strip()

        # 1. Check known process map
        target_exe = _PROCESS_MAP.get(query)

        # 2. Fuzzy match against process map keys if not found
        if not target_exe:
            matches = difflib.get_close_matches(query, _PROCESS_MAP.keys(), n=1, cutoff=0.55)
            if matches:
                target_exe = _PROCESS_MAP[matches[0]]

        killed = []
        for proc in psutil.process_iter(["name", "pid"]):
            proc_name = (proc.info["name"] or "").lower()
            if target_exe:
                if proc_name == target_exe.lower():
                    try:
                        proc.terminate()
                        killed.append(proc.info["name"])
                    except Exception:
                        pass
            else:
                # Fallback: substring match against all running process names
                if query in proc_name or proc_name.startswith(query[:4]):
                    try:
                        proc.terminate()
                        killed.append(proc.info["name"])
                    except Exception:
                        pass

        if killed:
            return True, killed[0]
        return False, None

    def list_apps(self):
        """Return sorted list of all indexed app names."""
        return sorted(self.registry.keys())
