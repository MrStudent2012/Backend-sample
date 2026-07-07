"""TaskFlow API main application."""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.config import APP_VERSION
from app.database import get_db, engine, Base
from app.models import User
from app.schemas import SignupRequest, SignupResponse
from app.services.auth import hash_password

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    version=APP_VERSION,
    description="A lightweight project & task management REST API"
)

@app.post(
    "/api/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"]
)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Hash the password
    hashed_password = hash_password(request.password)
    
    # Create new user
    new_user = User(
        username=request.username,
        hashed_password=hashed_password
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return SignupResponse(message="User created successfully", username=new_user.username)
