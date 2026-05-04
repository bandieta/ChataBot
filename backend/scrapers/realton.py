"""Scraper for Realton (realton.pl) — WordPress real estate plugin."""
import re
import requests
from bs4 import BeautifulSoup
from .base import Listing

LIST_URL = "https://realton.pl/nieruchomosci-na-sprzedaz/domy-na-sprzedaz/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape() -> list[Listing]:
    listings = []
    try:
        resp = requests.get(LIST_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.find_all(class_=re.compile(r"property_listing|property_card"))
        seen = set()

        for card in cards:
            a = card.find("a", href=re.compile(r"/oferta/"))
            if not a:
                continue
            url = a.get("href", "")
            if not url or url in seen:
                continue
            seen.add(url)

            h = card.find(["h2", "h3", "h4", "h5"])
            title = h.get_text(strip=True) if h else ""
            title = re.sub(r"\s*&…$", "…", title)
            if not title:
                continue

            loc_el = card.find(class_="property_location_image")
            location = loc_el.get_text(" ", strip=True).strip(" ,") if loc_el else ""

            price_el = card.find(class_="listing_unit_price_wrapper")
            price = None
            if price_el:
                m = re.search(r"([\d\s\xa0]+)\s*zł", price_el.get_text())
                if m:
                    price = int(re.sub(r"[\s\xa0]", "", m.group(1)))

            area = None
            area_el = card.find(class_="infosize")
            if area_el:
                m = re.search(r"(\d+(?:[,\.]\d+)?)\s*m", area_el.get_text())
                if m:
                    area = float(m.group(1).replace(",", "."))

            listings.append(Listing(
                agency="Realton",
                url=url,
                title=title,
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[Realton] scraper error: {e}")
    return listings
