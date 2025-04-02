from typing import Optional, List
from datetime import date, time, datetime
from pydantic import BaseModel

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    event_time: Optional[time] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    organizer: Optional[str] = None
    max_participants: Optional[int] = None
    registration_deadline: Optional[date] = None
    is_active: bool = True

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    organizer: Optional[str] = None
    max_participants: Optional[int] = None
    registration_deadline: Optional[date] = None
    is_active: Optional[bool] = None

class Event(EventBase):
    id: int
    created_at: datetime
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None
    participant_count: Optional[int] = None
    
    class Config:
        orm_mode = True

class EventParticipantBase(BaseModel):
    event_id: int
    attendance_status: str = "Registered"
    feedback: Optional[str] = None

class EventParticipantCreate(EventParticipantBase):
    pass

class EventParticipantUpdate(BaseModel):
    attendance_status: Optional[str] = None
    feedback: Optional[str] = None

class EventParticipant(EventParticipantBase):
    id: int
    alumni_id: int
    registration_date: datetime
    event_title: Optional[str] = None
    alumni_name: Optional[str] = None
    
    class Config:
        orm_mode = True