"""Scraper for Realton (realton.pl) — WordPress site, same pattern as REMA."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://realton.pl"
LIST_URL = f"{BASE}/nieruchomosci-na-sprzedaz/domy-na-sprzedaz/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = (
            soup.select(".property-listing")
            or soup.select("article.property")
            or soup.select(".offer-item")
        )
        if not cards:
            anchors = soup.find_all("a", href=re.compile(r"/oferta/[^/]+/?$"))
            cards = [a.find_parent(["article", "div", "li"]) for a in anchors if a.find_parent(["article", "div", "li"])]

        for card in cards:
            a = card.find("a", href=re.compile(r"/oferta/"))
            if not a:
                continue
            url = urljoin(BASE, a["href"])
            text = card.get_text(" ", strip=True)

            area_m = re.search(r"(\d+(?:[,\.]\d+)?)\s*m[²2]", text)
            area = float(area_m.group(1).replace(",", ".")) if area_m else None

            price_m = re.search(r"([\d\s\xa0]+)\s*zł", text)
            price = int(re.sub(r"\s|\xa0", "", price_m.group(1))) if price_m else None

            title = a.get_text(strip=True) or text[:80]

            loc_el = card.select_one("[class*='locat'], [class*='city'], [class*='address']")
            location = loc_el.get_text(strip=True) if loc_el else _extract_location(text)

            listings.append(Listing(
                agency="Realton",
                url=url,
                title=title.strip(),
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[Realton] scraper error: {e}")
    return listings


def _extract_location(text: str) -> str:
    m = re.search(r"(Katowice|Chorzów|Sosnowiec|Mysłowice|Tychy|Ruda Śląska|Mikołów|Bytom|Będzin|Czeladź)[^\d]*", text)
    return m.group(0).strip() if m else ""
