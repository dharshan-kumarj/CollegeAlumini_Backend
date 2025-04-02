from typing import Any
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.schemas.user import User, Token, UserCreate, UserUpdate
from app.services.auth import (
    get_user_by_email,
    create_user,
    update_user_last_login,
    refresh_access_token
)

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Update last login time
    update_user_last_login(db, user)
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id, expires_delta=refresh_token_expires),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    db: Session = Depends(get_db), refresh_token: str = None
) -> Any:
    """
    Refresh access token using a valid refresh token
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required",
        )
    
    tokens = refresh_access_token(db, refresh_token)
    return tokens

@router.post("/register", response_model=User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )
    
    user = create_user(db, user_in=user_in)
    return user

@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update current user
    """
    # Check if email already exists for another user
    if user_in.email and user_in.email != current_user.email:
        user_with_email = get_user_by_email(db, email=user_in.email)
        if user_with_email and user_with_email.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists",
            )
    
    # Update user
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user