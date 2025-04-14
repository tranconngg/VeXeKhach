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
