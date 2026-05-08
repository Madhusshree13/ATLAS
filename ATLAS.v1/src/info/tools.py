"""
info/tools.py — Weather (Open-Meteo) and Dictionary (dictionaryapi.dev)
Both APIs are free and require no API key.
"""

import requests
from urllib.parse import quote as _q

_TIMEOUT = 6  # seconds

# WMO weather interpretation codes → human description
_WMO = {
    0: "clear sky",
    1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "icy fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "moderate snow", 75: "heavy snow", 77: "snow grains",
    80: "light showers", 81: "showers", 82: "violent showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "severe thunderstorm",
}


def get_weather(city: str) -> dict:
    """
    Fetch current weather for `city` using Open-Meteo + its geocoding API.
    Returns a flat dict, or None on failure.
    """
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={_q(city)}&count=1&language=en&format=json",
            timeout=_TIMEOUT,
        ).json()
        if not geo.get("results"):
            return None
        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]

        w = requests.get(
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,apparent_temperature,weathercode,"
            "windspeed_10m,relativehumidity_2m"
            "&daily=temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max"
            "&timezone=auto&forecast_days=1",
            timeout=_TIMEOUT,
        ).json()

        cur   = w.get("current", {})
        daily = w.get("daily",   {})
        code  = cur.get("weathercode", -1)
        return {
            "city":        loc.get("name", city),
            "country":     loc.get("country", ""),
            "temp":        cur.get("temperature_2m"),
            "feels_like":  cur.get("apparent_temperature"),
            "humidity":    cur.get("relativehumidity_2m"),
            "wind_kmh":    cur.get("windspeed_10m"),
            "condition":   _WMO.get(code, "unknown conditions"),
            "high":        (daily.get("temperature_2m_max")  or [None])[0],
            "low":         (daily.get("temperature_2m_min")  or [None])[0],
            "rain_chance": (daily.get("precipitation_probability_max") or [None])[0],
        }
    except Exception as exc:
        print(f"[Weather] {exc}")
        return None


def define_word(word: str) -> str:
    """
    Look up `word` via dictionaryapi.dev.
    Returns a spoken-ready definition string, or None if not found.
    """
    try:
        resp = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{_q(word.lower().strip())}",
            timeout=_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data or not isinstance(data, list):
            return None

        entry    = data[0]
        meanings = entry.get("meanings", [])
        if not meanings:
            return None

        m    = meanings[0]
        pos  = m.get("partOfSpeech", "")
        defs = m.get("definitions", [])
        if not defs:
            return None

        defn    = defs[0].get("definition", "")
        example = defs[0].get("example", "")

        out = f"{entry.get('word', word)}"
        if pos:
            out += f", {pos}"
        out += f": {defn}"
        if example:
            out += f'. For example: "{example}"'
        return out
    except Exception as exc:
        print(f"[Dictionary] {exc}")
        return None
