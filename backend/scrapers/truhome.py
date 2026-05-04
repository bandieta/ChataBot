"""Scraper for TRUhome (truhome.eu) — custom PHP platform."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://www.truhome.eu"
LIST_URL = f"{BASE}/oferty-nieruchomosci,DOM-na-sprzeda%C5%BC.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        links = soup.find_all("a", href=re.compile(r"oferta-nieruchomosci,\d+"))
        seen = set()

        for link in links:
            href = link.get("href", "")
            id_m = re.search(r"oferta-nieruchomosci,(\d+)", href)
            if not id_m:
                continue
            listing_id = id_m.group(1)
            if listing_id in seen:
                continue
            seen.add(listing_id)

            url = urljoin(BASE, href)
            # Collect surrounding text for data
            card = link.find_parent(["div", "li", "article", "tr"]) or link
            text = card.get_text(" ", strip=True)

            area_m = re.search(r"(\d+(?:[,\.]\d+)?)\s*m[²2]", text)
            area = float(area_m.group(1).replace(",", ".")) if area_m else None

            price_m = re.search(r"([\d\s\xa0]+)\s*zł", text)
            price = int(re.sub(r"\s|\xa0", "", price_m.group(1))) if price_m else None

            title = link.get_text(strip=True) or f"Dom – TRUhome #{listing_id}"

            loc_m = re.search(r"(Katowice|Chorzów|Sosnowiec|Mysłowice|Tychy|Ruda Śląska|Mikołów|Bytom|Będzin|Czeladź|Siemianowice)[^\d,\n]*", text)
            location = loc_m.group(0).strip() if loc_m else ""

            listings.append(Listing(
                agency="TRUhome",
                url=url,
                title=title,
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[TRUhome] scraper error: {e}")
    return listings
