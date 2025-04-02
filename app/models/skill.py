from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<Skill {self.name}>"

class AlumniSkill(Base):
    __tablename__ = "alumni_skills"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency_level = Column(String(20), nullable=True)  # "Beginner", "Intermediate", etc.
    
    # Relationships
    alumni = relationship("Alumni", backref="skill_associations")
    skill = relationship("Skill", backref="alumni_associations")
    
    def __repr__(self):
        return f"<AlumniSkill {self.alumni_id} - {self.skill_id}>"