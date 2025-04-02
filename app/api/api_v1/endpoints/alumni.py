from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.api.deps import (
    get_db, get_current_user, get_current_alumni, get_current_college_admin
)
from app.models.user import User
from app.models.alumni import Alumni, AlumniConnection
from app.schemas.alumni import (
    AlumniCreate, AlumniUpdate, Alumni as AlumniSchema,
    AlumniRegistration, AlumniConnection as AlumniConnectionSchema,
    AlumniConnectionCreate, AlumniConnectionUpdate
)
from app.services.alumni_registration import register_alumni

router = APIRouter()

@router.post("/register", response_model=AlumniSchema)
def create_alumni_registration(
    *,
    db: Session = Depends(get_db),
    registration_in: AlumniRegistration,
) -> Any:
    """
    Register a new alumni with user account (self-registration)
    """
    # Check if email already exists
    user = db.query(User).filter(User.email == registration_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )
    
    alumni = register_alumni(db=db, registration=registration_in)
    return alumni

@router.get("/", response_model=List[AlumniSchema])
def read_alumni(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = None,
    country: Optional[str] = None,
    is_verified: Optional[bool] = None,
    batch_year: Optional[int] = None,
    department_id: Optional[int] = None,
    search: Optional[str] = Query(None, description="Search in first name, last name, email"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve alumni with optional filtering.
    """
    query = db.query(Alumni)
    
    # Apply filters if provided
    if city:
        query = query.filter(Alumni.city == city)
    if country:
        query = query.filter(Alumni.country == country)
    if is_verified is not None:
        query = query.filter(Alumni.is_verified == is_verified)
    
    # Filter by batch year if provided
    if batch_year:
        query = query.join(Alumni.education_records).filter(
            Education.batch_year_end == batch_year
        )
    
    # Filter by department if provided
    if department_id:
        query = query.join(Alumni.education_records).filter(
            Education.department_id == department_id
        )
    
    # Apply search if provided
    if search:
        query = query.join(User).filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    # Get paginated results
    alumni = query.offset(skip).limit(limit).all()
    
    return alumni

@router.get("/me", response_model=AlumniSchema)
def read_alumni_me(
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get current alumni profile
    """
    return current_alumni

@router.put("/me", response_model=AlumniSchema)
def update_alumni_me(
    *,
    db: Session = Depends(get_db),
    alumni_in: AlumniUpdate,
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update current alumni profile
    """
    # Update alumni profile
    for field, value in alumni_in.dict(exclude_unset=True).items():
        setattr(current_alumni, field, value)
    
    db.add(current_alumni)
    db.commit()
    db.refresh(current_alumni)
    return current_alumni

@router.post("/me/profile-picture", response_model=AlumniSchema)
async def upload_profile_picture(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Upload profile picture for current alumni
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Generate file path
    import os
    from uuid import uuid4
    from app.core.config import settings
    
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid4()}{file_extension}"
    file_path = f"media/alumni_profiles/{file_name}"
    
    # Save file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update alumni profile
    current_alumni.profile_picture = file_path
    db.add(current_alumni)
    db.commit()
    db.refresh(current_alumni)
    
    return current_alumni

@router.get("/{alumni_id}", response_model=AlumniSchema)
def read_alumni_by_id(
    alumni_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific alumni by ID
    """
    alumni = db.query(Alumni).filter(Alumni.id == alumni_id).first()
    if not alumni:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumni not found",
        )
    return alumni

@router.put("/{alumni_id}/verify", response_model=AlumniSchema)
def verify_alumni(
    alumni_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_college_admin)
) -> Any:
    """
    Verify an alumni (college admin only)
    """
    alumni = db.query(Alumni).filter(Alumni.id == alumni_id).first()
    if not alumni:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumni not found",
        )
    
    alumni.is_verified = True
    alumni.verified_by_id = current_admin.id
    alumni.verification_date = datetime.utcnow()
    
    db.add(alumni)
    db.commit()
    db.refresh(alumni)
    return alumni

# Alumni connections endpoints

@router.post("/connections", response_model=AlumniConnectionSchema)
def create_alumni_connection(
    *,
    db: Session = Depends(get_db),
    connection_in: AlumniConnectionCreate,
    current_alumni: Alumni = Depends(get_current_alumni)
) -> Any:
    """
    Create a connection request with another alumni
    """
    # Check if receiver exists
    receiver = db.query(Alumni).filter(Alumni.id == connection_in.receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver alumni not found",
        )
    
    # Check if connection already exists
    existing_connection = db.query(AlumniConnection).filter(
        or_(
            and_(AlumniConnection.initiator_id == current_alumni.id, 
                 AlumniConnection.receiver_id == connection_in.receiver_id),
            and_(AlumniConnection.initiator_id == connection_in.receiver_id,
                 AlumniConnection.receiver_id == current_alumni.id)
        )
    ).first()
    
    if existing_connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection already exists with status: {existing_connection.status}",
        )
    
    # Create connection request
    connection = AlumniConnection(
        initiator_id=current_alumni.id,
        receiver_id=connection_in.receiver_id,
        status="Pending"
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    return connection

@router.get("/connections/received", response_model=List[AlumniConnectionSchema])
def read_received_connections(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get connection requests received by current alumni
    """
    query = db.query(AlumniConnection).filter(AlumniConnection.receiver_id == current_alumni.id)
    
    if status:
        query = query.filter(AlumniConnection.status == status)
    
    connections = query.all()
    return connections

@router.get("/connections/initiated", response_model=List[AlumniConnectionSchema])
def read_initiated_connections(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Get connection requests initiated by current alumni
    """
    query = db.query(AlumniConnection).filter(AlumniConnection.initiator_id == current_alumni.id)
    
    if status:
        query = query.filter(AlumniConnection.status == status)
    
    connections = query.all()
    return connections

@router.put("/connections/{connection_id}", response_model=AlumniConnectionSchema)
def update_connection_status(
    connection_id: int,
    status_update: AlumniConnectionUpdate,
    db: Session = Depends(get_db),
    current_alumni: Alumni = Depends(get_current_alumni),
) -> Any:
    """
    Update status of a connection request (accept/reject/block)
    """
    connection = db.query(AlumniConnection).filter(
        AlumniConnection.id == connection_id,
        AlumniConnection.receiver_id == current_alumni.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found or you don't have permission to update it",
        )
    
    # Update status
    connection.status = status_update.status
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    return connection

@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_alumni: Alumni = Depends(get_current_alumni),
) -> None:  # Note the return type is None
    """
    Delete a connection
    """
    connection = db.query(AlumniConnection).filter(
        AlumniConnection.id == connection_id,
        or_(
            AlumniConnection.initiator_id == current_alumni.id,
            AlumniConnection.receiver_id == current_alumni.id
        )
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found or you don't have permission to delete it",
        )
    
    db.delete(connection)
    db.commit()
    
    # Don't return anything for 204 responses
    return  # Just return without any value

# Bulk import endpoints for college admin

@router.post("/import", response_model=dict)
def import_alumni_from_csv(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_college_admin),
) -> Any:
    """
    Import alumni from CSV file (college admin only)
    """
    from tempfile import NamedTemporaryFile
    import shutil
    from app.services.alumni_registration import preregister_alumni_from_csv
    
    # Save uploaded file to temporary file
    with NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Process the CSV file
        result = preregister_alumni_from_csv(db=db, csv_file_path=tmp_path)
        return {
            "message": "Alumni import completed",
            "created": result["created"],
            "updated": result["updated"]
        }
    finally:
        # Clean up the temp file
        import os
        os.unlink(tmp_path)