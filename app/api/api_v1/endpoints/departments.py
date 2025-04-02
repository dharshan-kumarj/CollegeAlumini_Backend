from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_college_admin
from app.models.user import User
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, Department as DepartmentSchema

router = APIRouter()

@router.get("/", response_model=List[DepartmentSchema])
def read_departments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve departments.
    """
    departments = db.query(Department).offset(skip).limit(limit).all()
    return departments

@router.post("/", response_model=DepartmentSchema)
def create_department(
    *,
    db: Session = Depends(get_db),
    department_in: DepartmentCreate,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Create new department (college admin only).
    """
    department = db.query(Department).filter(Department.name == department_in.name).first()
    if department:
        raise HTTPException(
            status_code=400,
            detail="Department with this name already exists",
        )
    
    department = Department(**department_in.dict())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

@router.get("/{department_id}", response_model=DepartmentSchema)
def read_department(
    *,
    db: Session = Depends(get_db),
    department_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get department by ID.
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.put("/{department_id}", response_model=DepartmentSchema)
def update_department(
    *,
    db: Session = Depends(get_db),
    department_id: int,
    department_in: DepartmentUpdate,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Update department (college admin only).
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # If name is being updated, check for uniqueness
    if department_in.name and department_in.name != department.name:
        existing = db.query(Department).filter(Department.name == department_in.name).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Department with this name already exists",
            )
    
    for field, value in department_in.dict(exclude_unset=True).items():
        setattr(department, field, value)
    
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    *,
    db: Session = Depends(get_db),
    department_id: int,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Delete department (college admin only).
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(department)
    db.commit()
    return None