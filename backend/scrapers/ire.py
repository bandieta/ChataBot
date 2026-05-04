"""Scraper for agencies using the IRE/OpenRem platform.

Listing URL pattern: /domy-na-sprzedaz-{price}zl-{area}m2-{location-slug}-o{id}
Area and price are encoded in the URL slug — no need to fetch detail pages.
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape_ire(agency_name: str, base_url: str) -> list[Listing]:
    url = f"{base_url}/oferty/domy/sprzedaz/"
    listings = []
    try:
        resp = requests.get(url, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        links = soup.find_all("a", href=re.compile(r"domy-na-sprzedaz-\d+zl-\d+m2-"))
        seen = set()

        for link in links:
            href = link.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)

            area_m = re.search(r"-(\d+)m2-", href)
            area = float(area_m.group(1)) if area_m else None

            price_m = re.search(r"-(\d+)zl-", href)
            price = int(price_m.group(1)) if price_m else None

            loc_m = re.search(r"\d+m2-(.+?)-o\d+", href)
            location_slug = loc_m.group(1) if loc_m else ""
            location = location_slug.replace("-", " ").title()

            full_url = urljoin(base_url + "/", href.lstrip("/"))

            title = link.get_text(strip=True) or f"Dom {area}m² – {location}"

            listings.append(Listing(
                agency=agency_name,
                url=full_url,
                title=title,
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[{agency_name}] scraper error: {e}")
    return listings
