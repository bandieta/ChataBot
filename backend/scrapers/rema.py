"""Scraper for REMA Nieruchomości (rema.nieruchomosci.pl)."""
import re
import requests
from bs4 import BeautifulSoup
from .base import Listing

LIST_URL = "https://rema.nieruchomosci.pl/oferta-domy-sprzedaz/"
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

            loc_el = card.find(class_="property_location_image")
            location = loc_el.get_text(" ", strip=True).strip(" ,") if loc_el else ""

            price_el = card.find(class_="listing_unit_price_wrapper")
            price = None
            if price_el:
                m = re.search(r"([\d,\s\xa0]+)\s*zł", price_el.get_text())
                if m:
                    price = int(re.sub(r"[,\s\xa0]", "", m.group(1)))

            area = None
            for item in card.find_all(class_="property_listing_details_v2_item"):
                m = re.search(r"(\d+(?:[,\.]\d+)?)\s*m", item.get_text())
                if m:
                    area = float(m.group(1).replace(",", "."))
                    break

            if not title:
                continue

            listings.append(Listing(
                agency="REMA",
                url=url,
                title=title,
                location=location,
                price=price,
                area=area,
            ))
    except Exception as e:
        print(f"[REMA] scraper error: {e}")
    return listings
