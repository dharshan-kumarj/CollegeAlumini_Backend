from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id", ondelete="SET NULL"), nullable=True)
    company_name = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    job_description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    location = Column(String(100), nullable=True)
    job_type = Column(String(20), nullable=True)  # "Full-time", "Part-time", etc.
    salary_range = Column(String(100), nullable=True)
    application_link = Column(String(255), nullable=True)
    contact_email = Column(String(100), nullable=True)
    posting_date = Column(Date, server_default=func.current_date())
    closing_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    alumni = relationship("Alumni", backref="job_postings")
    
    def __repr__(self):
        return f"<JobPosting {self.job_title} at {self.company_name}>"