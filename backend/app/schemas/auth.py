"""
AgriNova AI — Authentication schemas.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(None, max_length=20)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: str | None = Field(None, min_length=2, max_length=255)
    phone: str | None = Field(None, max_length=20)


class UserResponse(BaseModel):
    """Schema for user data in API responses."""

    id: str
    email: str
    full_name: str
    phone: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: str
    exp: int
