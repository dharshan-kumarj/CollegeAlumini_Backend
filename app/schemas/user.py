from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
import re

class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_alumni: bool
    is_college_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    refresh: Optional[bool] = False