"""Business logic for user operations."""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas import UserCreate


class UserNotFoundError(Exception):
    pass


class DuplicateEmailError(Exception):
    pass


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise DuplicateEmailError(f"User with email '{user_data.email}' already exists")

    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User:
    """Get a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError(f"User with id {user_id} not found")
    return user


def list_users(db: Session) -> list[User]:
    """List all users."""
    return db.query(User).order_by(User.name).all()
