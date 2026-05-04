"""FastAPI server exposing listings to the NextJS frontend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import db

db.init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "PATCH"],
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
