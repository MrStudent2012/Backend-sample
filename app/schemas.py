"""Pydantic schemas for request/response validation."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user signup request."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    created_at: datetime