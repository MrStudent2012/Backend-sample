"""Configuration for the TaskFlow API."""
from __future__ import annotations
import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
APP_ENV: str = os.getenv("APP_ENV", "development")
APP_VERSION = "1.2.0"

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100
