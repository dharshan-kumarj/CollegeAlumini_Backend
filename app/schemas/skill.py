from typing import Optional
from pydantic import BaseModel, validator

class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = None

class Skill(SkillBase):
    id: int
    
    class Config:
        orm_mode = True

class AlumniSkillBase(BaseModel):
    skill_id: int
    proficiency_level: Optional[str] = None
    
    @validator('proficiency_level')
    def validate_proficiency_level(cls, v):
        valid_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        if v and v not in valid_levels:
            raise ValueError(f'Proficiency level must be one of {valid_levels}')
        return v

class AlumniSkillCreate(AlumniSkillBase):
    pass

class AlumniSkillUpdate(BaseModel):
    proficiency_level: Optional[str] = None

class AlumniSkill(AlumniSkillBase):
    id: int
    alumni_id: int
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None
    
    class Config:
        orm_mode = True