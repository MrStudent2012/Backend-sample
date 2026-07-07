from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import engine, get_db, Base
from app.schemas import UserCreate, UserResponse
from app.crud import get_user_by_username, create_user

Base.metadata.create_all(bind=engine)


@app.post(
    "/api/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Create a new user account with username and password"
)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    
    - **username**: Unique username (3-50 characters, alphanumeric with _ and -)
    - **password**: Password (minimum 8 characters)
    
    Returns the created user information (excluding password).
    """
    # Check if username already exists
    existing_user = get_user_by_username(db, username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    try:
        db_user = create_user(db=db, user=user)
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            created_at=db_user.created_at
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )