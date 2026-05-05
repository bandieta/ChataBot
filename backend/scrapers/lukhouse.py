"""Scraper for LUK-HOUSE (luk-house.pl) — custom platform.

Listings are at /oferta/{id}-{ver}-{num}/{slug}. Area and price are not
in the URL, so we fetch each detail page and parse from the card text.
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://www.luk-house.pl"
LIST_URL = BASE + "/oferty/domy"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}
RENTAL_RE = re.compile(r"wynajem|do wynaj[eę]cia|na wynajem", re.IGNORECASE)


def _parse_number(text: str) -> float | None:
    m = re.search(r"(\d[\d\s]*(?:[,\.]\d+)?)", text.replace("\xa0", " "))
    if not m:
        return None
    return float(m.group(1).replace(" ", "").replace(",", "."))


def scrape() -> list[Listing]:
    listings = []
    seen_urls = set()
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        links = soup.find_all("a", href=re.compile(r"/oferta/"))
        offer_urls = []
        for a in links:
            href = a.get("href", "")
            full = urljoin(BASE + "/", href.lstrip("/"))
            if full not in seen_urls and not RENTAL_RE.search(href):
                seen_urls.add(full)
                offer_urls.append(full)

        for url in offer_urls:
            try:
                detail = requests.get(url, timeout=15, headers=HEADERS)
                detail.raise_for_status()
                dsoup = BeautifulSoup(detail.text, "html.parser")

                # Skip rentals
                page_text = dsoup.get_text(" ", strip=True)
                if RENTAL_RE.search(page_text):
                    continue

                # Area: "78,10 m2" or "78,10m²"
                area_m = re.search(r"Powierzchnia[^\d]*(\d[\d\s]*(?:[,\.]\d+)?)\s*m", page_text)
                area = float(area_m.group(1).replace(" ", "").replace(",", ".")) if area_m else None

                # Price in raw HTML: Cena<strong>485 000 PLN</strong>
                price_m = re.search(r"Cena<strong>([\d\s]+)PLN", detail.text)
                price = int(re.sub(r"\s+", "", price_m.group(1))) if price_m else None

                # Location: first word of slug is the city
                slug_m = re.search(r"/oferta/[^/]+/([^/]+)$", url)
                slug = slug_m.group(1) if slug_m else ""
                # slug like "bytom-wozniaka-..." → "Bytom"
                location = slug.split("-")[0].title() if slug else ""

                # Title from h2 (h1 is usually empty on this site); strip "Sprzedaż" suffix
                title_el = dsoup.find("h2") or dsoup.find("h1")
                raw_title = title_el.get_text(strip=True) if title_el else f"Dom – {location}"
                title = re.sub(r"\s*Sprzeda[żz]$", "", raw_title, flags=re.IGNORECASE)[:100]

                if area is None:
                    continue

                listings.append(Listing(
                    agency="LUK-HOUSE",
                    url=url,
                    title=title,
                    location=location,
                    price=price,
                    area=area,
                ))
            except Exception:
                continue

    except Exception as e:
        print(f"[LUK-HOUSE] scraper error: {e}")
    return listings
