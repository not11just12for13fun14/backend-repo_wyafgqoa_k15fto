"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Core user/profile
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    avatar: Optional[str] = Field(None, description="Avatar URL")
    phone: Optional[str] = Field(None)
    is_active: bool = Field(True)

class Friend(BaseModel):
    user_id: str = Field(..., description="User id of the owner")
    friend_id: str = Field(..., description="User id of the friend")
    status: Literal["pending","accepted","blocked"] = "pending"

# Venues and Events
class Venue(BaseModel):
    name: str
    type: Literal["court","studio","recovery"]
    tags: List[str] = []
    address: str
    rating: float = 4.5
    distance_km: float = 1.2
    price_per_30min: float = 10.0
    image: Optional[str] = None
    phone: Optional[str] = None

class Offer(BaseModel):
    title: str
    description: Optional[str] = None
    discount_percent: Optional[int] = None
    image: Optional[str] = None
    venue_type: Optional[Literal["court","studio","recovery"]] = None

class Event(BaseModel):
    title: str
    category: Literal["sports","dance","workshop","other"] = "sports"
    venue_id: Optional[str] = None
    date: Optional[str] = None
    price: float = 0.0
    image: Optional[str] = None

# Social/community
class Game(BaseModel):
    title: str
    sport: str
    visibility: Literal["public","private"] = "public"
    host_user_id: Optional[str] = None
    max_players: int = 10
    players: List[str] = []
    description: Optional[str] = None

class SocialPost(BaseModel):
    user_id: Optional[str] = None
    content: str
    image: Optional[str] = None

# Bookings
class Booking(BaseModel):
    user_id: Optional[str] = None
    venue_id: str
    venue_name: str
    venue_type: Literal["court","studio","recovery"]
    date: str
    start_time: str
    end_time: str
    slots: int = 1
    total_amount: float
    status: Literal["upcoming","completed","cancelled"] = "upcoming"
    share_to_social: bool = False

