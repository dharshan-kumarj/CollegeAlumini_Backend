from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, HttpUrl, validator

class JobPostingBase(BaseModel):
    company_name: str
    job_title: str
    job_description: str
    required_skills: Optional[str] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    application_link: Optional[HttpUrl] = None
    contact_email: Optional[EmailStr] = None
    closing_date: Optional[date] = None
    is_active: bool = True
    
    @validator('job_type')
    def validate_job_type(cls, v):
        valid_types = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Remote']
        if v and v not in valid_types:
            raise ValueError(f'Job type must be one of {valid_types}')
        return v

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: Optional[str] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    application_link: Optional[HttpUrl] = None
    contact_email: Optional[EmailStr] = None
    closing_date: Optional[date] = None
    is_active: Optional[bool] = None

class JobPosting(JobPostingBase):
    id: int
    alumni_id: Optional[int] = None
    posting_date: date
    posted_by_name: Optional[str] = None
    
    class Config:
        orm_mode = True