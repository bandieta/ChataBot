"""Scraper for WGN Katowice (katowice.wgn.pl)."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://katowice.wgn.pl"
LIST_URL = f"{BASE}/oferty/domy/sprzedaz"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # WGN uses article cards or list rows
        cards = soup.select("article, .offer-box, .listing-item, tr.offer")
        if not cards:
            links = soup.find_all("a", href=re.compile(r"/oferta/|/nieruchomosc/", re.I))
            cards = [a.find_parent(["div", "li", "article", "tr"]) for a in links if a.find_parent(["div", "li", "article", "tr"])]

        seen = set()
        for card in cards:
            a = card.find("a", href=True)
            if not a:
                continue
            url = urljoin(BASE, a["href"])
            if url in seen:
                continue
            seen.add(url)

            text = card.get_text(" ", strip=True)
            area_m = re.search(r"(\d+(?:[,\.]\d+)?)\s*m[²2]", text)
            area = float(area_m.group(1).replace(",", ".")) if area_m else None

            price_m = re.search(r"([\d\s\xa0]+)\s*zł", text)
            price = int(re.sub(r"\s|\xa0", "", price_m.group(1))) if price_m else None

            title = a.get_text(strip=True) or text[:80]

            loc_m = re.search(
                r"(Katowice|Chorzów|Sosnowiec|Mysłowice|Tychy|Ruda Śląska|Mikołów|Bytom|Będzin|Czeladź|Siemianowice)[^\d,\n]*",
                text,
            )
            location = loc_m.group(0).strip() if loc_m else ""

            listings.append(Listing(
                agency="WGN Katowice",
                url=url,
                title=title.strip(),
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[WGN Katowice] scraper error: {e}")
    return listings
