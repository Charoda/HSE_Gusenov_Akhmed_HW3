from pydantic import BaseModel, EmailStr, HttpUrl, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LinkBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(None, max_length=50)
    expires_at: Optional[datetime] = None


class LinkCreate(LinkBase):
    pass


class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    custom_alias: Optional[str] = Field(None, max_length=50)
    expires_at: Optional[datetime] = None


class LinkResponse(LinkBase):
    id: int
    short_code: str
    clicks: int
    last_clicked_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class LinkStats(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime
    clicks: int
    last_clicked_at: Optional[datetime] = None
    is_active: bool
    expires_at: Optional[datetime] = None


class LinkSearch(BaseModel):
    original_url: HttpUrl


class LinkSearchResponse(LinkResponse):
    pass