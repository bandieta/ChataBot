"""Scraper for Indexo (indexo.com.pl)."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://www.indexo.com.pl"
LIST_URL = f"{BASE}/oferty_nieruchomosci,DOM.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.find_all(class_="listaofert_lista")
        seen = set()

        for card in cards:
            a = card.find("a", href=re.compile(r"oferta-nieruchomosci,\d+"))
            if not a:
                continue
            href = a.get("href", "")
            url = urljoin(BASE, href)
            if url in seen:
                continue
            seen.add(url)

            text = card.get_text(" ", strip=True)

            area_m = re.search(r"pow\.:\s*(\d+(?:[,\.]\d+)?)\s*m", text)
            if not area_m:
                area_m = re.search(r"(\d+(?:[,\.]\d+)?)\s*m[²2]", text)
            area = float(area_m.group(1).replace(",", ".")) if area_m else None

            price_m = re.search(r"cena:\s*([\d\s\xa0]+)\s*zł", text, re.IGNORECASE)
            if not price_m:
                price_m = re.search(r"([\d\s\xa0]+)\s*zł", text)
            price = int(re.sub(r"[\s\xa0]", "", price_m.group(1))) if price_m else None

            # Title from URL slug: strip leading type prefix
            slug = re.sub(r"oferta-nieruchomosci,\d+,", "", href)
            slug = slug.replace(".html", "").replace("-", " ").strip()
            slug = re.sub(r"oferta sprzedazy domu w ", "", slug, flags=re.IGNORECASE)
            title = slug.capitalize()[:80] if slug else f"Dom – Indexo"

            loc_m = re.search(
                r"(Katowice|Chorzów|Sosnowiec|Mysłowice|Tychy|Ruda Śląska|Mikołów|Bytom|Będzin|Czeladź|Siemianowice)[^\d,\n]*",
                text,
            )
            location = loc_m.group(0).strip() if loc_m else ""

            listings.append(Listing(
                agency="Indexo",
                url=url,
                title=title,
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[Indexo] scraper error: {e}")
    return listings
