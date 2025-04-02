from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(100), nullable=False)
    batch_year_start = Column(Integer, nullable=False)
    batch_year_end = Column(Integer, nullable=False)
    major = Column(String(100), nullable=True)
    minor = Column(String(100), nullable=True)
    gpa = Column(Float, nullable=True)
    achievements = Column(Text, nullable=True)
    
    # Relationships
    alumni = relationship("Alumni", backref="education_records")
    department = relationship("Department")
    
    def __repr__(self):
        return f"<Education {self.degree} - {self.alumni_id}>"