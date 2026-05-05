"""Scraper for agencies using the offer-card platform (DOMEX, MLYNARSCY, etc.).

URL slug pattern: /domy-na-sprzedaz-{price}zl-{area}m2-{location}/{id}
Area and price parsed from slug, no detail page needed.
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Listing

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)"}


def scrape_offer_card(agency_name: str, base_url: str, listing_path: str = "/oferty/domy") -> list[Listing]:
    listings = []
    page = 1
    seen = set()
    try:
        while True:
            sep = "&" if "?" in listing_path else "?"
            url = base_url.rstrip("/") + "/" + listing_path.lstrip("/") + f"{sep}page={page - 1}"
            resp = requests.get(url, timeout=15, headers=HEADERS)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.find_all(class_=re.compile(r"offer-card"))
            if not cards:
                break

            new_this_page = 0
            for card in cards:
                a = card.find("a", href=re.compile(r"domy-na-sprzedaz-\d+zl-\d+m2-"))
                if not a:
                    continue
                href = a.get("href", "")
                full_url = urljoin(base_url + "/", href.lstrip("/"))
                if full_url in seen:
                    continue
                seen.add(full_url)
                new_this_page += 1

                area_m = re.search(r"-(\d+(?:[,\.]\d+)?)m2-", href)
                area = float(area_m.group(1).replace(",", ".")) if area_m else None

                price_m = re.search(r"-(\d+)zl-", href)
                price = int(price_m.group(1)) if price_m else None

                loc_m = re.search(r"\d+m2-(.+?)(?:/\d+|$)", href)
                location_slug = loc_m.group(1) if loc_m else ""
                location = location_slug.replace("-", " ").title().strip("/")

                title_el = card.find(class_=re.compile(r"title|name|heading", re.I)) or a
                title = title_el.get_text(strip=True)[:100] or f"Dom {area}m² – {location}"

                listings.append(Listing(
                    agency=agency_name,
                    url=full_url,
                    title=title,
                    location=location,
                    price=price,
                    area=area,
                ))

            if new_this_page == 0:
                break
            page += 1
            if page > 20:
                break

    except Exception as e:
        print(f"[{agency_name}] scraper error: {e}")
    return listings
