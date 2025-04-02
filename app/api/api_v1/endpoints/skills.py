from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_alumni, get_current_college_admin
from app.models.user import User
from app.models.skill import Skill, AlumniSkill
from app.schemas.skill import (
    SkillCreate, SkillUpdate, Skill as SkillSchema,
    AlumniSkillCreate, AlumniSkillUpdate, AlumniSkill as AlumniSkillSchema
)

router = APIRouter()

# Skills endpoints
@router.get("/", response_model=List[SkillSchema])
def read_skills(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, description="Search in skill name or category"),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve skills.
    """
    query = db.query(Skill)
    
    if search:
        query = query.filter(
            (Skill.name.ilike(f"%{search}%")) | (Skill.category.ilike(f"%{search}%"))
        )
    
    skills = query.offset(skip).limit(limit).all()
    return skills

@router.post("/", response_model=SkillSchema)
def create_skill(
    *,
    db: Session = Depends(get_db),
    skill_in: SkillCreate,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Create new skill (admin only).
    """
    skill = db.query(Skill).filter(Skill.name == skill_in.name).first()
    if skill:
        raise HTTPException(
            status_code=400,
            detail="Skill with this name already exists",
        )
    
    skill = Skill(**skill_in.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

@router.get("/{skill_id}", response_model=SkillSchema)
def read_skill(
    *,
    db: Session = Depends(get_db),
    skill_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get skill by ID.
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.put("/{skill_id}", response_model=SkillSchema)
def update_skill(
    *,
    db: Session = Depends(get_db),
    skill_id: int,
    skill_in: SkillUpdate,
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Update skill (admin only).
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # If name is being updated, check for uniqueness
    if skill_in.name and skill_in.name != skill.name:
        existing = db.query(Skill).filter(Skill.name == skill_in.name).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Skill with this name already exists",
            )
    
    for field, value in skill_in.dict(exclude_unset=True).items():
        setattr(skill, field, value)
    
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

# Alumni skills endpoints
@router.post("/my-skills", response_model=AlumniSkillSchema)
def create_alumni_skill(
    *,
    db: Session = Depends(get_db),
    skill_in: AlumniSkillCreate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Add a skill to alumni's profile.
    """
    # Check if skill exists
    skill = db.query(Skill).filter(Skill.id == skill_in.skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )
    
    # Check if already added
    existing = db.query(AlumniSkill).filter(
        AlumniSkill.alumni_id == current_alumni.id,
        AlumniSkill.skill_id == skill_in.skill_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This skill is already added to your profile",
        )
    
    alumni_skill = AlumniSkill(**skill_in.dict(), alumni_id=current_alumni.id)
    db.add(alumni_skill)
    db.commit()
    db.refresh(alumni_skill)
    
    # Add skill details for response
    alumni_skill.skill_name = skill.name
    alumni_skill.skill_category = skill.category
    
    return alumni_skill

@router.get("/my-skills", response_model=List[AlumniSkillSchema])
def read_alumni_skills(
    *,
    db: Session = Depends(get_db),
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get skills for current alumni.
    """
    alumni_skills = db.query(AlumniSkill).filter(
        AlumniSkill.alumni_id == current_alumni.id
    ).all()
    
    # Add skill details for response
    for as_item in alumni_skills:
        skill = db.query(Skill).filter(Skill.id == as_item.skill_id).first()
        as_item.skill_name = skill.name
        as_item.skill_category = skill.category
    
    return alumni_skills

@router.put("/my-skills/{skill_id}", response_model=AlumniSkillSchema)
def update_alumni_skill(
    *,
    db: Session = Depends(get_db),
    skill_id: int,
    skill_update: AlumniSkillUpdate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update proficiency level for a skill.
    """
    alumni_skill = db.query(AlumniSkill).filter(
        AlumniSkill.skill_id == skill_id,
        AlumniSkill.alumni_id == current_alumni.id
    ).first()
    
    if not alumni_skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found in your profile",
        )
    
    for field, value in skill_update.dict(exclude_unset=True).items():
        setattr(alumni_skill, field, value)
    
    db.add(alumni_skill)
    db.commit()
    db.refresh(alumni_skill)
    
    # Add skill details for response
    skill = db.query(Skill).filter(Skill.id == alumni_skill.skill_id).first()
    alumni_skill.skill_name = skill.name
    alumni_skill.skill_category = skill.category
    
    return alumni_skill

@router.delete("/my-skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alumni_skill(
    *,
    db: Session = Depends(get_db),
    skill_id: int,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Remove a skill from alumni's profile.
    """
    alumni_skill = db.query(AlumniSkill).filter(
        AlumniSkill.skill_id == skill_id,
        AlumniSkill.alumni_id == current_alumni.id
    ).first()
    
    if not alumni_skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found in your profile",
        )
    
    db.delete(alumni_skill)
    db.commit()
    return None