"""FastAPI server exposing listings to the NextJS frontend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
import asyncio
import json
import db

db.init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "https://dagora.tech"],
    allow_methods=["GET", "PATCH", "POST"],
    allow_headers=["*"],
)


@app.get("/listings")
def list_listings(agency: Optional[str] = None):
    return db.get_all(agency)


@app.get("/agencies")
def list_agencies():
    rows = db.get_all()
    return sorted({r["agency"] for r in rows})


@app.patch("/listings/{listing_id}/interest")
def toggle_interest(listing_id: int, interested: bool):
    db.set_interested(listing_id, interested)
    return {"ok": True}


def _run_scrapers_sync() -> dict:
    import geocoder
    from scrapers import get_all_scrapers

    AREA_MIN, AREA_MAX = 100.0, 180.0
    total = 0
    nearby = 0
    new_added = 0

    for scraper in get_all_scrapers():
        try:
            listings = scraper()
            total += len(listings)
            for listing in listings:
                if listing.area is None or not (AREA_MIN <= listing.area <= AREA_MAX):
                    continue
                if listing.lat and listing.lng:
                    dist = geocoder._haversine(
                        geocoder.KATOWICE_LAT, geocoder.KATOWICE_LON,
                        listing.lat, listing.lng,
                    )
                else:
                    dist = geocoder.distance_from_katowice(listing.location)
                if dist > geocoder.MAX_DISTANCE_KM:
                    continue
                nearby += 1
                if db.is_known(listing.url):
                    continue
                db.insert(
                    url=listing.url,
                    agency=listing.agency,
                    title=listing.title,
                    location=listing.location,
                    price=listing.price,
                    area=listing.area,
                    distance_km=dist,
                )
                new_added += 1
        except Exception as e:
            print(f"[scrape] {e}")

    return {"total": total, "nearby": nearby, "new": new_added}


@app.post("/scrape")
async def scrape_now():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _run_scrapers_sync)
    return result


async def _scrape_event_gen():
    import geocoder
    from scrapers import get_all_scrapers

    AREA_MIN, AREA_MAX = 100.0, 180.0
    loop = asyncio.get_event_loop()
    total = nearby = new_added = 0

    for scraper in get_all_scrapers():
        try:
            listings = await loop.run_in_executor(None, scraper)
            total += len(listings)
            for listing in listings:
                area_ok = listing.area is not None and AREA_MIN <= listing.area <= AREA_MAX
                if listing.lat and listing.lng:
                    dist = geocoder._haversine(
                        geocoder.KATOWICE_LAT, geocoder.KATOWICE_LON,
                        listing.lat, listing.lng,
                    )
                else:
                    dist = geocoder.distance_from_katowice(listing.location)
                dist_ok = dist != float("inf") and dist <= geocoder.MAX_DISTANCE_KM
                matched = area_ok and dist_ok
                if matched:
                    nearby += 1
                    if not db.is_known(listing.url):
                        db.insert(
                            url=listing.url,
                            agency=listing.agency,
                            title=listing.title,
                            location=listing.location,
                            price=listing.price,
                            area=listing.area,
                            distance_km=dist,
                        )
                        new_added += 1
                reason = None if matched else ("metraż" if not area_ok else "odległość")
                event = {
                    "agency": listing.agency,
                    "title": listing.title[:80] if listing.title else "",
                    "url": listing.url,
                    "area": listing.area,
                    "price": listing.price,
                    "location": listing.location,
                    "distance": None if dist == float("inf") else round(dist, 1),
                    "matched": matched,
                    "reason": reason,
                }
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[stream] {e}")

    yield f"data: {json.dumps({'type': 'done', 'total': total, 'nearby': nearby, 'new': new_added})}\n\n"


@app.get("/scrape/stream")
async def scrape_stream():
    return StreamingResponse(
        _scrape_event_gen(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
