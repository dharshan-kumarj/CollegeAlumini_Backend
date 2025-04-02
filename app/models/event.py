from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date, Time, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(Date, nullable=False)
    event_time = Column(Time, nullable=True)
    location = Column(String(255), nullable=True)
    event_type = Column(String(50), nullable=True)
    organizer = Column(String(100), nullable=True)
    max_participants = Column(Integer, nullable=True)
    registration_deadline = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<Event {self.title}>"

class EventParticipant(Base):
    __tablename__ = "event_participants"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    alumni_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    attendance_status = Column(String(20), default="Registered")  # "Registered", "Attended", etc.
    feedback = Column(Text, nullable=True)
    
    # Relationships
    event = relationship("Event", backref="participants")
    alumni = relationship("Alumni", backref="event_participations")
    
    def __repr__(self):
        return f"<EventParticipant {self.alumni_id} - {self.event_id}>"