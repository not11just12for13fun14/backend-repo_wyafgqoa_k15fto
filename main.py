import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db

app = FastAPI(title="Sports Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------- Models for requests ---------
class BookingIn(BaseModel):
    user_id: Optional[str] = None
    venue_id: str
    venue_name: str
    venue_type: str
    date: str
    start_time: str
    end_time: str
    slots: int
    total_amount: float
    share_to_social: bool = False

class GameIn(BaseModel):
    title: str
    sport: str
    visibility: str = "public"
    host_user_id: Optional[str] = None
    max_players: int = 10
    description: Optional[str] = None

class PostIn(BaseModel):
    user_id: Optional[str] = None
    content: str
    image: Optional[str] = None


# --------- Basic health ---------
@app.get("/")
def root():
    return {"message": "Sports Hub API running"}


# --------- Seed/sample data (in-memory for catalogs) ---------
SAMPLE_OFFERS = [
    {"id": "o1", "title": "Weekend Smash 30% OFF", "description": "On all football turfs", "image": "https://images.unsplash.com/photo-1603297637585-4eb3b0c6c3b1"},
    {"id": "o2", "title": "Studio Saver 20%", "description": "Dance & Zumba", "image": "https://images.unsplash.com/photo-1571907480495-2416503cf842"},
    {"id": "o3", "title": "Recovery Combo", "description": "Ice bath + Massage", "image": "https://images.unsplash.com/photo-1556227701-787edf1a6e47"},
]

SAMPLE_VENUES = [
    {"id": "v1", "name": "City Arena", "type": "court", "tags": ["football","basketball"], "address": "Downtown", "rating": 4.8, "distance_km": 1.1, "price_per_30min": 15, "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b"},
    {"id": "v2", "name": "Hoops Central", "type": "court", "tags": ["basketball"], "address": "West End", "rating": 4.6, "distance_km": 2.0, "price_per_30min": 12, "image": "https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5"},
    {"id": "v3", "name": "Groove Studio", "type": "studio", "tags": ["dance","zumba"], "address": "Midtown", "rating": 4.7, "distance_km": 0.9, "price_per_30min": 10, "image": "https://images.unsplash.com/photo-1515169067865-5387ec356754"},
    {"id": "v4", "name": "Wellness Hub", "type": "recovery", "tags": ["ice bath","massage"], "address": "Riverside", "rating": 4.9, "distance_km": 1.5, "price_per_30min": 18, "image": "https://images.unsplash.com/photo-1519824145371-296894a0daa9"},
    {"id": "v5", "name": "Blue Pools", "type": "recovery", "tags": ["swimming"], "address": "Uptown", "rating": 4.5, "distance_km": 2.2, "price_per_30min": 8, "image": "https://images.unsplash.com/photo-1519315901367-f34ff9154487"},
]

SAMPLE_EVENTS = [
    {"id": "e1", "title": "Local League Finals", "category": "sports", "date": "2025-11-30", "price": 5, "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b"},
    {"id": "e2", "title": "Zumba Marathon", "category": "dance", "date": "2025-12-05", "price": 12, "image": "https://images.unsplash.com/photo-1549576490-b0b4831ef60a"},
    {"id": "e3", "title": "Strength Workshop", "category": "workshop", "date": "2025-12-10", "price": 20, "image": "https://images.unsplash.com/photo-1554284126-aa88f22d8b74"},
]

SAMPLE_ACTIVITIES = [
    {"id": "a1", "type": "booked", "text": "You booked City Arena - Football"},
    {"id": "a2", "type": "joined", "text": "You joined 3v3 Basketball"},
    {"id": "a3", "type": "hosted", "text": "You hosted Zumba Jam"},
]


# --------- Catalog endpoints ---------
@app.get("/api/offers")
async def get_offers():
    return SAMPLE_OFFERS


@app.get("/api/venues")
async def get_venues(vtype: Optional[str] = None, tag: Optional[str] = None):
    items = SAMPLE_VENUES
    if vtype:
        items = [v for v in items if v["type"] == vtype]
    if tag:
        items = [v for v in items if tag in v.get("tags", [])]
    return items


@app.get("/api/events")
async def get_events(category: Optional[str] = None):
    items = SAMPLE_EVENTS
    if category:
        items = [e for e in items if e["category"] == category]
    return items


@app.get("/api/activities/recent")
async def recent_activities():
    return SAMPLE_ACTIVITIES


# --------- Bookings & recommendations (persisted) ---------
@app.post("/api/bookings")
async def create_booking(payload: BookingIn):
    try:
        booking_id = create_document("booking", payload.dict())
        result = {"id": booking_id, **payload.dict()}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bookings")
async def list_bookings(user_id: Optional[str] = None):
    try:
        filt = {"user_id": user_id} if user_id else {}
        docs = get_documents("booking", filt)
        # stringify ids
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/recovery")
async def recommend_recovery():
    # Top picks from recovery type
    recos = [v for v in SAMPLE_VENUES if v["type"] == "recovery"][:3]
    return {"title": "Top picks to recover", "items": recos}


# --------- Social: games & posts (persisted) ---------
@app.get("/api/games")
async def list_games():
    try:
        docs = get_documents("game")
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception:
        return []


@app.post("/api/games")
async def create_game(payload: GameIn):
    try:
        gid = create_document("game", payload.dict())
        return {"id": gid, **payload.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/posts")
async def list_posts():
    try:
        docs = get_documents("socialpost")
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception:
        return []


@app.post("/api/posts")
async def create_post(payload: PostIn):
    try:
        pid = create_document("socialpost", payload.dict())
        return {"id": pid, **payload.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Diagnostics ---------
@app.get("/test")
async def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "❌ Not Available"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
