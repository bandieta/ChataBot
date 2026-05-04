"""Scraper for Indexo (indexo.com.pl) — PHP site with query-string search."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
from .base import Listing

BASE = "https://www.indexo.com.pl"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}

LIST_URL = (
    f"{BASE}/wyszukiwarka_wynik.php"
    "?rodzajnieruchomosci=DOM&rodzajtransakcji=SPRZEDA%C5%BC"
)


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find links to individual listings
        links = soup.find_all("a", href=re.compile(r"oferta|nieruchomosc|wynik_szczegoly", re.I))
        if not links:
            # Broader fallback
            links = soup.find_all("a", href=re.compile(r"\.php\?"))

        seen = set()
        for link in links:
            href = link.get("href", "")
            url = urljoin(BASE, href)
            if url in seen or url == LIST_URL:
                continue
            seen.add(url)

            card = link.find_parent(["tr", "div", "li", "article"]) or link
            text = card.get_text(" ", strip=True)

            area_m = re.search(r"(\d+(?:[,\.]\d+)?)\s*m[²2]", text)
            area = float(area_m.group(1).replace(",", ".")) if area_m else None

            price_m = re.search(r"([\d\s\xa0]+)\s*zł", text)
            price = int(re.sub(r"\s|\xa0", "", price_m.group(1))) if price_m else None

            title = link.get_text(strip=True) or f"Dom – Indexo"

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
