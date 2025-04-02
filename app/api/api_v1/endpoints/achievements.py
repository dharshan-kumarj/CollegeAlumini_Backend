from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_alumni
from app.models.achievement import Achievement
from app.schemas.achievement import AchievementCreate, AchievementUpdate, Achievement as AchievementSchema

router = APIRouter()

@router.post("/", response_model=AchievementSchema)
def create_achievement(
    *,
    db: Session = Depends(get_db),
    achievement_in: AchievementCreate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Create achievement record for the current alumni.
    """
    achievement = Achievement(**achievement_in.dict(), alumni_id=current_alumni.id)
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement

@router.get("/", response_model=List[AchievementSchema])
def read_achievements(
    *,
    db: Session = Depends(get_db),
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Retrieve achievement records for the current alumni.
    """
    achievements = db.query(Achievement).filter(
        Achievement.alumni_id == current_alumni.id
    ).order_by(Achievement.achievement_date.desc()).all()
    
    return achievements

@router.get("/{achievement_id}", response_model=AchievementSchema)
def read_achievement(
    *,
    db: Session = Depends(get_db),
    achievement_id: int,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get specific achievement record.
    """
    achievement = db.query(Achievement).filter(
        Achievement.id == achievement_id, 
        Achievement.alumni_id == current_alumni.id
    ).first()
    
    if not achievement:
        raise HTTPException(
            status_code=404,
            detail="Achievement record not found",
        )
    
    return achievement

@router.put("/{achievement_id}", response_model=AchievementSchema)
def update_achievement(
    *,
    db: Session = Depends(get_db),
    achievement_id: int,
    achievement_in: AchievementUpdate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update achievement record.
    """
    achievement = db.query(Achievement).filter(
        Achievement.id == achievement_id, 
        Achievement.alumni_id == current_alumni.id
    ).first()
    
    if not achievement:
        raise HTTPException(
            status_code=404,
            detail="Achievement record not found",
        )
    
    for field, value in achievement_in.dict(exclude_unset=True).items():
        setattr(achievement, field, value)
    
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement

@router.delete("/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_achievement(
    *,
    db: Session = Depends(get_db),
    achievement_id: int,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Delete achievement record.
    """
    achievement = db.query(Achievement).filter(
        Achievement.id == achievement_id, 
        Achievement.alumni_id == current_alumni.id
    ).first()
    
    if not achievement:
        raise HTTPException(
            status_code=404,
            detail="Achievement record not found",
        )
    
    db.delete(achievement)
    db.commit()
    return None