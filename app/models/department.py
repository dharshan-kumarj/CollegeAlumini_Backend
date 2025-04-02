from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    hod_name = Column(String(100), nullable=True)
    established_year = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Department {self.name}>"