"""Scraper for BestNest (bestnest.pl).

List page returns article.download-card elements with area and price in card text.
URL slug: /nieruchomosci/dom-na-sprzedaz/{city}/{id}
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

BASE = "https://bestnest.pl"
LIST_URL = (
    BASE + "/lista-ofert/sprzeda%C5%BC"
    "?searchIndex=1&sort=add_date_desc&main_type_id=1&transaction=131"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=20, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article", class_="download-card")

        for card in cards:
            link = card.find("a", href=re.compile(r"/nieruchomosci/dom-na-sprzedaz/"))
            if not link:
                continue
            href = link.get("href", "")
            full_url = urljoin(BASE + "/", href.lstrip("/"))

            city_m = re.search(r"/dom-na-sprzedaz/([^/]+)/", href)
            location = city_m.group(1).replace("-", " ").title() if city_m else ""

            text = card.get_text(" ", strip=True)

            area_m = re.search(r"Powierzchnia:\s*(\d+(?:[,\.]\d+)?)\s*m", text)
            area = float(area_m.group(1).replace(",", ".")) if area_m else None

            # Use first PLN text node (total price, not per-m² price)
            price_nodes = [
                s.strip() for s in card.strings
                if "PLN" in s and re.search(r"\d", s)
            ]
            price = None
            if price_nodes:
                pm = re.search(r"([\d\s]+),\d{2}\s*PLN", price_nodes[0])
                price = int(re.sub(r"\s", "", pm.group(1))) if pm else None

            title_el = card.find(class_=re.compile(r"title|name|heading", re.I))
            title = title_el.get_text(strip=True)[:100] if title_el else f"Dom – {location}"

            if area is None:
                continue

            listings.append(Listing(
                agency="BestNest",
                url=full_url,
                title=title,
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[BestNest] scraper error: {e}")
    return listings
