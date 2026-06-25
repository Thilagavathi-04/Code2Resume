import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    github_url: Optional[str] = None
    github_token: Optional[str] = None
    linkedin_id: Optional[str] = None
    leetcode_id: Optional[str] = None
    mobile_number: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    github_url: Optional[str] = None
    github_token: Optional[str] = None
    linkedin_id: Optional[str] = None
    leetcode_id: Optional[str] = None
    mobile_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_id: Optional[str] = None
    leetcode_id: Optional[str] = None
    mobile_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
