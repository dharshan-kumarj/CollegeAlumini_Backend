from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.core.database import Base

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    achievement_date = Column(Date, nullable=True)
    achievement_type = Column(String(50), nullable=True)
    organization = Column(String(100), nullable=True)
    reference_link = Column(String(255), nullable=True)
    
    # Relationships
    alumni = relationship("Alumni", backref="achievements")
    
    def __repr__(self):
        return f"<Achievement {self.title} - {self.alumni_id}>"