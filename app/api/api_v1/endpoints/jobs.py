from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db, get_current_user, get_current_alumni, get_current_college_admin
from app.models.user import User
from app.models.job import JobPosting
from app.schemas.job import JobPostingCreate, JobPostingUpdate, JobPosting as JobPostingSchema

router = APIRouter()

@router.get("/", response_model=List[JobPostingSchema])
def read_job_postings(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    company: Optional[str] = None,
    job_type: Optional[str] = None,
    is_active: bool = True,
    location: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search in title, company, or description"),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve job postings with filters.
    """
    query = db.query(JobPosting)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(JobPosting.is_active == is_active)
    if company:
        query = query.filter(JobPosting.company_name == company)
    if job_type:
        query = query.filter(JobPosting.job_type == job_type)
    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))
    
    # Apply search
    if search:
        query = query.filter(
            or_(
                JobPosting.job_title.ilike(f"%{search}%"),
                JobPosting.company_name.ilike(f"%{search}%"),
                JobPosting.job_description.ilike(f"%{search}%")
            )
        )
    
    # Get paginated results, most recent first
    jobs = query.order_by(JobPosting.posting_date.desc()).offset(skip).limit(limit).all()
    
    # Add posted_by_name field
    for job in jobs:
        if job.alumni:
            job.posted_by_name = f"{job.alumni.user.first_name} {job.alumni.user.last_name}"
    
    return jobs

@router.post("/", response_model=JobPostingSchema)
def create_job_posting(
    *,
    db: Session = Depends(get_db),
    job_in: JobPostingCreate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Create a job posting.
    """
    job = JobPosting(**job_in.dict(), alumni_id=current_alumni.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Add posted_by_name for response
    job.posted_by_name = f"{current_alumni.user.first_name} {current_alumni.user.last_name}"
    
    return job

@router.get("/{job_id}", response_model=JobPostingSchema)
def read_job_posting(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a specific job posting.
    """
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found",
        )
    
    # Add posted_by_name for response
    if job.alumni:
        job.posted_by_name = f"{job.alumni.user.first_name} {job.alumni.user.last_name}"
    
    return job

@router.put("/{job_id}", response_model=JobPostingSchema)
def update_job_posting(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    job_in: JobPostingUpdate,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update a job posting.
    """
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.alumni_id == current_alumni.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found or you don't have permission to update it",
        )
    
    for field, value in job_in.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Add posted_by_name for response
    job.posted_by_name = f"{current_alumni.user.first_name} {current_alumni.user.last_name}"
    
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_posting(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a job posting.
    """
    job = None
    
    # Check if admin or job owner
    if current_user.is_college_admin:
        job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    else:
        # Find alumni profile for current user
        alumni = db.query(Alumni).filter(Alumni.user_id == current_user.id).first()
        if alumni:
            job = db.query(JobPosting).filter(
                JobPosting.id == job_id,
                JobPosting.alumni_id == alumni.id
            ).first()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found or you don't have permission to delete it",
        )
    
    db.delete(job)
    db.commit()
    return None

@router.get("/my-postings", response_model=List[JobPostingSchema])
def read_my_job_postings(
    *,
    db: Session = Depends(get_db),
    is_active: Optional[bool] = None,
    current_alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get job postings created by the current alumni.
    """
    query = db.query(JobPosting).filter(JobPosting.alumni_id == current_alumni.id)
    
    if is_active is not None:
        query = query.filter(JobPosting.is_active == is_active)
    
    jobs = query.order_by(JobPosting.posting_date.desc()).all()
    
    # Add posted_by_name for response
    for job in jobs:
        job.posted_by_name = f"{current_alumni.user.first_name} {current_alumni.user.last_name}"
    
    return jobs