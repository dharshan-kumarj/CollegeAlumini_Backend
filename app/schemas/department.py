from typing import Optional
from pydantic import BaseModel

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    hod_name: Optional[str] = None
    established_year: Optional[int] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None

class Department(DepartmentBase):
    id: int
    
    class Config:
        orm_mode = True