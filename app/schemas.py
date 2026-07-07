"""Pydantic schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user signup request."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for the account"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password for the account (minimum 8 characters)"
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.strip():
            raise ValueError("Username cannot be empty or only whitespace")
        return v.strip()


class UserResponse(BaseModel):
    """Schema for user response (excludes password)."""
    
    id: int
    username: str
