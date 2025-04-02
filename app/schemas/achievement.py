from typing import Optional
from datetime import date
from pydantic import BaseModel, HttpUrl

class AchievementBase(BaseModel):
    title: str
    description: Optional[str] = None
    achievement_date: Optional[date] = None
    achievement_type: Optional[str] = None
    organization: Optional[str] = None
    reference_link: Optional[HttpUrl] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    achievement_date: Optional[date] = None
    achievement_type: Optional[str] = None
    organization: Optional[str] = None
    reference_link: Optional[HttpUrl] = None

class Achievement(AchievementBase):
    id: int
    alumni_id: int
    
    class Config:
        orm_mode = True