from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.api.deps import get_db, get_current_user, get_current_alumni, get_current_college_admin
from app.models.user import User
from app.models.alumni import Alumni
from app.models.event import Event, EventParticipant
from app.schemas.event import (
    EventCreate, EventUpdate, Event as EventSchema,
    EventParticipantCreate, EventParticipantUpdate, EventParticipant as EventParticipantSchema
)

router = APIRouter()

@router.get("/", response_model=List[EventSchema])
def read_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    upcoming: bool = False,
    past: bool = False,
    event_type: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search in title or description"),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve events with filters.
    """
    query = db.query(Event)
    
    # Apply date filters
    today = date.today()
    if upcoming:
        query = query.filter(Event.event_date >= today)
    if past:
        query = query.filter(Event.event_date < today)
    
    # Apply event type filter
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    # Apply search
    if search:
        query = query.filter(
            or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%")
            )
        )
    
    # Sort by date, with upcoming events first
    query = query.order_by(Event.event_date.asc())
    
    # Get events with participant count
    events = query.offset(skip).limit(limit).all()
    
    # Add participant count and created by name
    for event in events:
        event.participant_count = db.query(func.count(EventParticipant.id)).filter(
            EventParticipant.event_id == event.id
        ).scalar()
        
        if event.created_by_id:
            creator = db.query(User).filter(User.id == event.created_by_id).first()
            event.created_by_name = f"{creator.first_name} {creator.last_name}" if creator else None
    
    return events

@router.post("/", response_model=EventSchema)
def create_event(
    *,
    db: Session = Depends(get_db),
    event_in: EventCreate,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Create new event (admin only).
    """
    event = Event(**event_in.dict(), created_by_id=current_admin.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Add additional fields for response
    event.participant_count = 0
    event.created_by_name = f"{current_admin.first_name} {current_admin.last_name}"
    
    return event

@router.get("/{event_id}", response_model=EventSchema)
def read_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get event by ID.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Add participant count and created by name
    event.participant_count = db.query(func.count(EventParticipant.id)).filter(
        EventParticipant.event_id == event.id
    ).scalar()
    
    if event.created_by_id:
        creator = db.query(User).filter(User.id == event.created_by_id).first()
        event.created_by_name = f"{creator.first_name} {creator.last_name}" if creator else None
    
    return event

@router.put("/{event_id}", response_model=EventSchema)
def update_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    event_in: EventUpdate,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Update event (admin only).
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for field, value in event_in.dict(exclude_unset=True).items():
        setattr(event, field, value)
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Add participant count and created by name
    event.participant_count = db.query(func.count(EventParticipant.id)).filter(
        EventParticipant.event_id == event.id
    ).scalar()
    
    if event.created_by_id:
        creator = db.query(User).filter(User.id == event.created_by_id).first()
        event.created_by_name = f"{creator.first_name} {creator.last_name}" if creator else None
    
    return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Delete event (admin only).
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return None

# Event participation endpoints
@router.post("/register", response_model=EventParticipantSchema)
def register_for_event(
    *,
    db: Session = Depends(get_db),
    registration_in: EventParticipantCreate,
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Register alumni for an event.
    """
    # Check if event exists and is active
    event = db.query(Event).filter(
        Event.id == registration_in.event_id,
        Event.is_active == True
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found or not active",
        )
    
    # Check if event is in the future
    today = date.today()
    if event.event_date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot register for past events",
        )
    
    # Check if registration deadline has passed
    if event.registration_deadline and event.registration_deadline < today:
        raise HTTPException(
            status_code=400,
            detail="Registration deadline has passed",
        )
    
    # Check if already registered
    existing = db.query(EventParticipant).filter(
        EventParticipant.event_id == registration_in.event_id,
        EventParticipant.alumni_id == current_alumni.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already registered for this event",
        )
    
    # Check if event is at capacity
    if event.max_participants:
        participant_count = db.query(func.count(EventParticipant.id)).filter(
            EventParticipant.event_id == event.id
        ).scalar()
        
        if participant_count >= event.max_participants:
            raise HTTPException(
                status_code=400,
                detail="Event has reached maximum capacity",
            )
    
    # Create registration
    participant = EventParticipant(
        event_id=registration_in.event_id,
        alumni_id=current_alumni.id,
        attendance_status=registration_in.attendance_status,
        feedback=registration_in.feedback
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    # Add additional fields for response
    participant.event_title = event.title
    participant.alumni_name = f"{current_alumni.user.first_name} {current_alumni.user.last_name}"
    
    return participant

@router.get("/my-registrations", response_model=List[EventParticipantSchema])
def read_my_registrations(
    *,
    db: Session = Depends(get_db),
    upcoming: bool = False,
    past: bool = False,
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get events the current alumni is registered for.
    """
    query = db.query(EventParticipant).filter(EventParticipant.alumni_id == current_alumni.id)
    
    if upcoming or past:
        query = query.join(Event)
        today = date.today()
        
        if upcoming:
            query = query.filter(Event.event_date >= today)
        if past:
            query = query.filter(Event.event_date < today)
    
    participations = query.all()
    
    # Add event and alumni details for response
    for p in participations:
        event = db.query(Event).filter(Event.id == p.event_id).first()
        p.event_title = event.title if event else None
        p.alumni_name = f"{current_alumni.user.first_name} {current_alumni.user.last_name}"
    
    return participations

@router.put("/my-registrations/{event_id}", response_model=EventParticipantSchema)
def update_registration(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    update_in: EventParticipantUpdate,
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update registration status or provide feedback.
    """
    participation = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.alumni_id == current_alumni.id
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=404,
            detail="Registration not found",
        )
    
    for field, value in update_in.dict(exclude_unset=True).items():
        setattr(participation, field, value)
    
    db.add(participation)
    db.commit()
    db.refresh(participation)
    
    # Add event and alumni details for response
    event = db.query(Event).filter(Event.id == participation.event_id).first()
    participation.event_title = event.title if event else None
    participation.alumni_name = f"{current_alumni.user.first_name} {current_alumni.user.last_name}"
    
    return participation

@router.delete("/my-registrations/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Cancel registration for an event.
    """
    participation = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.alumni_id == current_alumni.id
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=404,
            detail="Registration not found",
        )
    
    # Check if event is in the future
    event = db.query(Event).filter(Event.id == event_id).first()
    today = date.today()
    
    if event and event.event_date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel registration for past events",
        )
    
    db.delete(participation)
    db.commit()
    return None