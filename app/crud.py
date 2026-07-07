"""CRUD operations for database interactions."""
from __future__ import annotations

from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from app.auth import hash_password


def get_user_by_username(db: Session, username: str) -> User | None:
    """Retrieve a user by username."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with hashed password."""
    hashed_password = hash_password(user.password)
    
    db_user = User(
        username=user.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user