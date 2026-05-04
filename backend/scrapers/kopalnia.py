"""Scraper for Kopalnia Nieruchomości (kopalnia-nieruchomosci.pl)."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://kopalnia-nieruchomosci.pl"
LIST_URL = f"{BASE}/nieruchomosci/domy/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}

# Slug: /dom-sprzedaz-{area}m2-{price}pln-{location-parts}-slaskie,{id}/...
SLUG_RE = re.compile(r"dom-sprzedaz-(\d+)m2-(\d+)pln-(.+?)-slaskie", re.I)

CITY_MAP = {
    "katowice": "Katowice",
    "chorzow": "Chorzów",
    "sosnowiec": "Sosnowiec",
    "myslowice": "Mysłowice",
    "tychy": "Tychy",
    "ruda-slaska": "Ruda Śląska",
    "mikolow": "Mikołów",
    "bytom": "Bytom",
    "bedzin": "Będzin",
    "czeladz": "Czeladź",
    "siemianowice-slaskie": "Siemianowice Śląskie",
    "dabrowa-gornicza": "Dąbrowa Górnicza",
    "jaworzno": "Jaworzno",
    "swietochlowice": "Świętochłowice",
    "zabrze": "Zabrze",
    "gliwice": "Gliwice",
}


def _location_from_slug(slug: str) -> str:
    for key, name in CITY_MAP.items():
        if key in slug:
            return name
    # Fallback: last 1-2 parts of slug
    parts = slug.strip("-").split("-")
    return " ".join(p.capitalize() for p in parts[-2:])


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        links = soup.find_all("a", href=SLUG_RE)
        seen = set()

        for link in links:
            href = link.get("href", "")
            url = urljoin(BASE, href)
            if url in seen:
                continue
            seen.add(url)

            m = SLUG_RE.search(href)
            if not m:
                continue
            area = float(m.group(1))
            price = int(m.group(2))
            location = _location_from_slug(m.group(3))
            title = f"Dom {area:.0f}m² – {location}"

            listings.append(Listing(
                agency="Kopalnia Nieruchomości",
                url=url,
                title=title,
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[Kopalnia] scraper error: {e}")
    return listings
