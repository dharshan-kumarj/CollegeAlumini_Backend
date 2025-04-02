from sqlalchemy import Boolean, Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Alumni(Base):
    __tablename__ = "alumni"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone = Column(String(15), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    verified_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="alumni_profile")
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    
    def __repr__(self):
        return f"<Alumni {self.id}>"

class AlumniConnection(Base):
    __tablename__ = "alumni_connections"

    id = Column(Integer, primary_key=True, index=True)
    initiator_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False)
    connection_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="Pending")  # "Pending", "Accepted", "Rejected", "Blocked"
    
    # Relationships
    initiator = relationship("Alumni", foreign_keys=[initiator_id], backref="initiated_connections")
    receiver = relationship("Alumni", foreign_keys=[receiver_id], backref="received_connections")
    
    def __repr__(self):
        return f"<AlumniConnection {self.initiator_id} -> {self.receiver_id}: {self.status}>"