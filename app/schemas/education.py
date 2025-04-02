from typing import Optional
from pydantic import BaseModel, validator

class EducationBase(BaseModel):
    department_id: int
    degree: str
    batch_year_start: int
    batch_year_end: int
    major: Optional[str] = None
    minor: Optional[str] = None
    gpa: Optional[float] = None
    achievements: Optional[str] = None
    
    @validator('batch_year_end')
    def end_year_after_start_year(cls, v, values):
        if 'batch_year_start' in values and v < values['batch_year_start']:
            raise ValueError('End year must be after start year')
        return v
    
    @validator('gpa')
    def validate_gpa(cls, v):
        if v is not None and (v < 0 or v > 4.0):
            raise ValueError('GPA must be between 0 and 4.0')
        return v

class EducationCreate(EducationBase):
    pass

class EducationUpdate(BaseModel):
    department_id: Optional[int] = None
    degree: Optional[str] = None
    batch_year_start: Optional[int] = None
    batch_year_end: Optional[int] = None
    major: Optional[str] = None
    minor: Optional[str] = None
    gpa: Optional[float] = None
    achievements: Optional[str] = None

class Education(EducationBase):
    id: int
    alumni_id: int
    department_name: Optional[str] = None
    
    class Config:
        orm_mode = True