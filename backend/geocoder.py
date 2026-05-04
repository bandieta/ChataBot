import math
import json
import os
import time
import unicodedata
import requests

KATOWICE_LAT = 50.2649
KATOWICE_LON = 19.0238
MAX_DISTANCE_KM = 15.0

# Pre-computed distances (km) from Katowice center for Silesian cities
_CITY_KM = {
    "katowice": 0.0,
    "chorzow": 6.1,
    "siemianowice slaskie": 6.7,
    "siemianowice": 6.7,
    "myslowice": 10.2,
    "tychy": 15.3,
    "ruda slaska": 11.5,
    "swietochlowice": 9.5,
    "bytom": 14.7,
    "zabrze": 19.3,
    "sosnowiec": 8.4,
    "czeladz": 6.3,
    "mikolow": 13.1,
    "piekary slaskie": 14.4,
    "bedzin": 8.3,
    "dabrowa gornicza": 14.9,
    "jaworzno": 20.2,
    "gliwice": 25.2,
    "tarnowskie gory": 22.3,
    "bielsko biala": 55.0,
    "czestochowa": 72.0,
    "siewierz": 28.0,
    "pszczyna": 28.0,
    "rybnik": 45.0,
    "knurow": 30.0,
    "jastrzebie zdroj": 50.0,
    "zory": 45.0,
    "wodzislaw slaski": 50.0,
    "raciborz": 65.0,
    "zawiercie": 40.0,
    "olkusz": 35.0,
    "oswiecim": 45.0,
    "krakow": 75.0,
    "wroclaw": 155.0,
    "lodz": 165.0,
    "warszawa": 290.0,
    "poznan": 260.0,
    "gdansk": 480.0,
}

_CACHE_PATH = os.path.join(os.path.dirname(__file__), "geocache.json")
_cache: dict[str, float] = {}


def _load_cache():
    global _cache
    if os.path.exists(_CACHE_PATH):
        with open(_CACHE_PATH) as f:
            _cache = json.load(f)


def _save_cache():
    with open(_CACHE_PATH, "w") as f:
        json.dump(_cache, f)


_load_cache()


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _nominatim(location: str) -> float:
    key = _normalize(location)
    if key in _cache:
        return _cache[key]
    try:
        time.sleep(1)  # Nominatim rate limit
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{location}, Śląsk, Polska", "format": "json", "limit": 1},
            headers={"User-Agent": "ChataBot/1.0"},
            timeout=10,
        )
        data = resp.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            dist = _haversine(KATOWICE_LAT, KATOWICE_LON, lat, lon)
            _cache[key] = dist
            _save_cache()
            return dist
    except Exception as e:
        print(f"Nominatim error for '{location}': {e}")
    _cache[key] = float("inf")
    _save_cache()
    return float("inf")


def distance_from_katowice(location: str) -> float:
    """Returns distance in km from Katowice center."""
    if not location:
        return float("inf")

    norm = _normalize(location).replace("-", " ").replace(",", " ")
    words = norm.split()

    # Try longest prefix match first
    for length in range(min(len(words), 4), 0, -1):
        candidate = " ".join(words[:length])
        if candidate in _CITY_KM:
            return _CITY_KM[candidate]

    # Nominatim fallback
    return _nominatim(location)


def is_within_range(location: str) -> bool:
    return distance_from_katowice(location) <= MAX_DISTANCE_KM
