from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: Optional[str]
    username: str
    email: str
    created_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    is_email_verified: Optional[bool] = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = "unknown"
    age: Optional[int] = None
    phone_number: Optional[str] = "unknown"
    address: Optional[str] = "unknown"
    created_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    is_email_verified: Optional[bool] = False

class RouteBase(BaseModel):
    route_code: str
    departure: str
    destination: str
    price: float
    duration: int  # Thời gian di chuyển tính bằng phút
    distance: float  # Khoảng cách tính bằng km
    description: Optional[str] = None

class RouteCreate(RouteBase):
    pass

class RouteResponse(RouteBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class BusBase(BaseModel):
    bus_number: str
    capacity: int
    route_id: str
    departure_time: datetime
    arrival_time: datetime
    status: str  # available, in_transit, maintenance
    description: Optional[str] = None

class BusCreate(BusBase):
    pass

class BusResponse(BusBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class SeatBase(BaseModel):
    seat_number: str
    bus_id: str
    is_available: bool = True
    price: float

class SeatResponse(SeatBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
