from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_alumni
from app.models.employment import Employment
from app.schemas.employment import EmploymentCreate, EmploymentUpdate, Employment as EmploymentSchema

router = APIRouter()

@router.post("/", response_model=EmploymentSchema)
def create_employment(
    *,
    db: Session = Depends(get_db),
    employment_in: EmploymentCreate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Create employment record for the current alumni.
    """
    # If this is a current job, update all other jobs to not current
    if employment_in.is_current:
        db.query(Employment).filter(
            Employment.alumni_id == current_alumni.id,
            Employment.is_current == True
        ).update({"is_current": False})
    
    employment = Employment(**employment_in.dict(), alumni_id=current_alumni.id)
    db.add(employment)
    db.commit()
    db.refresh(employment)
    return employment

@router.get("/", response_model=List[EmploymentSchema])
def read_employments(
    *,
    db: Session = Depends(get_db),
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Retrieve employment records for the current alumni.
    """
    employments = db.query(Employment).filter(
        Employment.alumni_id == current_alumni.id
    ).order_by(Employment.is_current.desc(), Employment.start_date.desc()).all()
    
    return employments

@router.get("/{employment_id}", response_model=EmploymentSchema)
def read_employment(
    *,
    db: Session = Depends(get_db),
    employment_id: int,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get specific employment record.
    """
    employment = db.query(Employment).filter(
        Employment.id == employment_id, 
        Employment.alumni_id == current_alumni.id
    ).first()
    
    if not employment:
        raise HTTPException(
            status_code=404,
            detail="Employment record not found",
        )
    
    return employment

@router.put("/{employment_id}", response_model=EmploymentSchema)
def update_employment(
    *,
    db: Session = Depends(get_db),
    employment_id: int,
    employment_in: EmploymentUpdate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update employment record.
    """
    employment = db.query(Employment).filter(
        Employment.id == employment_id, 
        Employment.alumni_id == current_alumni.id
    ).first()
    
    if not employment:
        raise HTTPException(
            status_code=404,
            detail="Employment record not found",
        )
    
    # If updating to current job, update all other jobs to not current
    if employment_in.is_current and employment_in.is_current != employment.is_current:
        db.query(Employment).filter(
            Employment.alumni_id == current_alumni.id,
            Employment.is_current == True,
            Employment.id != employment_id
        ).update({"is_current": False})
    
    for field, value in employment_in.dict(exclude_unset=True).items():
        setattr(employment, field, value)
    
    db.add(employment)
    db.commit()
    db.refresh(employment)
    return employment

@router.delete("/{employment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employment(
    *,
    db: Session = Depends(get_db),
    employment_id: int,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Delete employment record.
    """
    employment = db.query(Employment).filter(
        Employment.id == employment_id, 
        Employment.alumni_id == current_alumni.id
    ).first()
    
    if not employment:
        raise HTTPException(
            status_code=404,
            detail="Employment record not found",
        )
    
    db.delete(employment)
    db.commit()
    return None