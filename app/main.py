"""Main FastAPI application for TaskFlow API."""

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.config import APP_VERSION
from app.database import engine, get_db, Base
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    version=APP_VERSION,
    description="A lightweight project & task management REST API"
)


@app.get("/")
def read_root():
    """Service information endpoint."""
    return {
        "service": "TaskFlow API",
        "version": APP_VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    
    - **username**: Unique username for the account (3-50 characters)
    - **password**: Password for the account (minimum 8 characters)
    
    Returns the created user details (excluding password).
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
