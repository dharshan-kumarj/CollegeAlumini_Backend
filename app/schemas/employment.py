from typing import Optional
from datetime import date
from pydantic import BaseModel, validator

class EmploymentBase(BaseModel):
    company_name: str
    job_title: str
    industry: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    location: Optional[str] = None
    
    @validator('employment_type')
    def validate_employment_type(cls, v):
        valid_types = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance']
        if v and v not in valid_types:
            raise ValueError(f'Employment type must be one of {valid_types}')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        if 'is_current' in values and values['is_current'] and v:
            raise ValueError('End date must be None if is_current is True')
        return v
    
    @validator('is_current')
    def validate_is_current(cls, v, values):
        if v and 'end_date' in values and values['end_date']:
            raise ValueError('is_current must be False if end_date is provided')
        return v

class EmploymentCreate(EmploymentBase):
    pass

class EmploymentUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    location: Optional[str] = None

class Employment(EmploymentBase):
    id: int
    alumni_id: int
    
    class Config:
        orm_mode = True