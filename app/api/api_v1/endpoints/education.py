from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_alumni, get_current_college_admin
from app.models.education import Education
from app.schemas.education import EducationCreate, EducationUpdate, Education as EducationSchema

router = APIRouter()

@router.post("/", response_model=EducationSchema)
def create_education(
    *,
    db: Session = Depends(get_db),
    education_in: EducationCreate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Create education record for the current alumni.
    """
    education = Education(**education_in.dict(), alumni_id=current_alumni.id)
    db.add(education)
    db.commit()
    db.refresh(education)
    
    # Add department name for response
    education.department_name = education.department.name
    
    return education

@router.get("/", response_model=List[EducationSchema])
def read_educations(
    *,
    db: Session = Depends(get_db),
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Retrieve education records for the current alumni.
    """
    educations = db.query(Education).filter(Education.alumni_id == current_alumni.id).all()
    
    # Add department names for response
    for edu in educations:
        edu.department_name = edu.department.name
    
    return educations

@router.get("/{education_id}", response_model=EducationSchema)
def read_education(
    *,
    db: Session = Depends(get_db),
    education_id: int,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get specific education record.
    """
    education = db.query(Education).filter(
        Education.id == education_id, 
        Education.alumni_id == current_alumni.id
    ).first()
    
    if not education:
        raise HTTPException(
            status_code=404,
            detail="Education record not found",
        )
    
    # Add department name for response
    education.department_name = education.department.name
    
    return education

@router.put("/{education_id}", response_model=EducationSchema)
def update_education(
    *,
    db: Session = Depends(get_db),
    education_id: int,
    education_in: EducationUpdate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update education record.
    """
    education = db.query(Education).filter(
        Education.id == education_id, 
        Education.alumni_id == current_alumni.id
    ).first()
    
    if not education:
        raise HTTPException(
            status_code=404,
            detail="Education record not found",
        )
    
    for field, value in education_in.dict(exclude_unset=True).items():
        setattr(education, field, value)
    
    db.add(education)
    db.commit()
    db.refresh(education)
    
    # Add department name for response
    education.department_name = education.department.name
    
    return education

@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(
    *,
    db: Session = Depends(get_db),
    education_id: int,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Delete education record.
    """
    education = db.query(Education).filter(
        Education.id == education_id, 
        Education.alumni_id == current_alumni.id
    ).first()
    
    if not education:
        raise HTTPException(
            status_code=404,
            detail="Education record not found",
        )
    
    db.delete(education)
    db.commit()
    return None

# Admin endpoints for education records

@router.get("/admin/alumni/{alumni_id}", response_model=List[EducationSchema])
def read_alumni_educations(
    *,
    db: Session = Depends(get_db),
    alumni_id: int,
    current_admin = Depends(get_current_college_admin),
) -> Any:
    """
    Retrieve education records for a specific alumni (admin only).
    """
    educations = db.query(Education).filter(Education.alumni_id == alumni_id).all()
    
    # Add department names for response
    for edu in educations:
        edu.department_name = edu.department.name
    
    return educations