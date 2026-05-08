"""
media_control.py — System media and volume control via Windows Virtual Key codes.
Uses only ctypes (stdlib) — no external packages required.
"""

import ctypes

_KEYEVENTF_KEYUP = 0x0002

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_MUTE      = 0xAD
VK_VOLUME_UP        = 0xAF
VK_VOLUME_DOWN      = 0xAE


def _press(vk: int):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, _KEYEVENTF_KEYUP, 0)


def play_pause():
    """Toggle play/pause on any focused media player (Spotify, YouTube, etc.)."""
    _press(VK_MEDIA_PLAY_PAUSE)


def next_track():
    """Skip to the next track."""
    _press(VK_MEDIA_NEXT_TRACK)


def prev_track():
    """Go back to the previous track."""
    _press(VK_MEDIA_PREV_TRACK)


def mute():
    """Toggle system mute."""
    _press(VK_VOLUME_MUTE)


def volume_up(steps: int = 5):
    """Increase volume by `steps` key presses (≈2% each on default Windows)."""
    for _ in range(steps):
        _press(VK_VOLUME_UP)


def volume_down(steps: int = 5):
    """Decrease volume by `steps` key presses."""
    for _ in range(steps):
        _press(VK_VOLUME_DOWN)


def set_volume_percent(percent: int):
    """
    Set system volume to an absolute percentage (0–100).
    Strategy: drive to 0 (50 DOWN presses), then step up to target.
    Each UP press ≈ 2% on Windows default; 50 steps covers 0–100%.
    """
    percent = max(0, min(100, percent))
    for _ in range(50):
        _press(VK_VOLUME_DOWN)
    steps = round(percent / 2)
    for _ in range(steps):
        _press(VK_VOLUME_UP)
