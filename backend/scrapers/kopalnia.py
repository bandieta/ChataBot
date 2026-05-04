"""Scraper for Kopalnia Nieruchomości (kopalnia-nieruchomosci.pl)."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://kopalnia-nieruchomosci.pl"
LIST_URL = f"{BASE}/nieruchomosci/domy/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # URL pattern: /dom-sprzedaz-{area}m2-{price}pln-...-slaskie,{id}/...
        links = soup.find_all("a", href=re.compile(r"dom-sprzedaz-\d+m2-\d+pln-"))
        if not links:
            links = soup.find_all("a", href=re.compile(r"/nieruchomosci/"))

        seen = set()
        for link in links:
            href = link.get("href", "")
            url = urljoin(BASE, href)
            if url in seen:
                continue
            seen.add(url)

            area_m = re.search(r"dom-sprzedaz-(\d+)m2-", href)
            area = float(area_m.group(1)) if area_m else None

            price_m = re.search(r"m2-(\d+)pln-", href)
            price = int(price_m.group(1)) if price_m else None

            # Location from URL slug
            loc_m = re.search(r"pln-(.+?)-slaskie", href)
            location_slug = loc_m.group(1) if loc_m else ""
            location = location_slug.replace("-", " ").title()

            card = link.find_parent(["div", "li", "article"]) or link
            text = card.get_text(" ", strip=True)
            title = link.get_text(strip=True) or f"Dom {area}m² – {location}"

            # Refine area/price from card text if URL parsing failed
            if area is None:
                area_m2 = re.search(r"(\d+(?:[,\.]\d+)?)\s*m[²2]", text)
                area = float(area_m2.group(1).replace(",", ".")) if area_m2 else None
            if price is None:
                price_m2 = re.search(r"([\d\s\xa0]+)\s*zł", text)
                price = int(re.sub(r"\s|\xa0", "", price_m2.group(1))) if price_m2 else None

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
