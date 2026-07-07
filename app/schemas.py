"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, field_validator

class SignupRequest(BaseModel):
    """Request schema for user signup."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, description="User password")
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username contains only alphanumeric characters and underscores."""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v

class SignupResponse(BaseModel):
    """Response schema for successful signup."""
    message: str
    username: str
