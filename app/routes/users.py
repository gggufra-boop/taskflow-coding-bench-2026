"""User API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.services.user_service import (
    DuplicateEmailError,
    UserNotFoundError,
    create_user,
    get_user,
    list_users,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user_endpoint(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        return create_user(db, user_data)
    except DuplicateEmailError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=list[UserResponse])
def list_users_endpoint(db: Session = Depends(get_db)):
    """List all users."""
    return list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    try:
        return get_user(db, user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
