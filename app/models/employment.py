from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from app.core.database import Base

class Employment(Base):
    __tablename__ = "employment"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    industry = Column(String(100), nullable=True)
    employment_type = Column(String(20), nullable=True)  # "Full-time", "Part-time", etc.
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    
    # Relationships
    alumni = relationship("Alumni", backref="employment_records")
    
    def __repr__(self):
        return f"<Employment {self.job_title} at {self.company_name} - {self.alumni_id}>"