"""Configuration for the TaskFlow API."""

from __future__ import annotations

import os


DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
APP_ENV: str = os.getenv("APP_ENV", "development")
APP_VERSION: str = "1.2.0"
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

# Authentication configuration
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30