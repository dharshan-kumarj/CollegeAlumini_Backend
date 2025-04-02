from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, validator, HttpUrl

from app.schemas.user import User
from app.schemas.education import Education
from app.schemas.employment import Employment
from app.schemas.skill import AlumniSkill
from app.schemas.achievement import Achievement

class AlumniBase(BaseModel):
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    
    @validator('gender')
    def validate_gender(cls, v):
        valid_genders = ['Male', 'Female', 'Other', 'Prefer not to say']
        if v and v not in valid_genders:
            raise ValueError(f'Gender must be one of {valid_genders}')
        return v

class AlumniCreate(AlumniBase):
    pass

class AlumniUpdate(AlumniBase):
    pass

class AlumniInDBBase(AlumniBase):
    id: int
    user_id: int
    registration_date: datetime
    is_active: bool
    is_verified: bool
    verification_date: Optional[datetime] = None
    verified_by_id: Optional[int] = None
    profile_picture: Optional[str] = None
    
    class Config:
        orm_mode = True

class Alumni(AlumniInDBBase):
    user: User
    education_records: Optional[List[Education]] = []
    employment_records: Optional[List[Employment]] = []
    skill_associations: Optional[List[AlumniSkill]] = []
    achievements: Optional[List[Achievement]] = []

class AlumniRegistration(BaseModel):
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None

class AlumniConnectionBase(BaseModel):
    receiver_id: int

class AlumniConnectionCreate(AlumniConnectionBase):
    pass

class AlumniConnection(AlumniConnectionBase):
    id: int
    initiator_id: int
    connection_date: datetime
    status: str
    
    class Config:
        orm_mode = True

class AlumniConnectionUpdate(BaseModel):
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['Pending', 'Accepted', 'Rejected', 'Blocked']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v