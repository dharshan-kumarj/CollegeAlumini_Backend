from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, *, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, *, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        username=user_in.username,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_last_login(db: Session, user: User) -> User:
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def refresh_access_token(db: Session, refresh_token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("refresh") is not True:
            raise ValueError("Not a refresh token")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        return {
            "access_token": create_access_token(user.id, expires_delta=access_token_expires),
            "refresh_token": create_refresh_token(user.id, expires_delta=refresh_token_expires),
            "token_type": "bearer",
        }
    except (JWTError, ValueError) as e:
        # Handle token validation errors
        raise ValueError(f"Invalid refresh token: {str(e)}")