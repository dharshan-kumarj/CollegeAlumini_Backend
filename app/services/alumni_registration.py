import csv
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.models.alumni import Alumni
from app.models.department import Department
from app.models.education import Education
from app.schemas.alumni import AlumniRegistration

def register_alumni(db: Session, *, registration: AlumniRegistration) -> Alumni:
    """
    Register a new alumni with user account
    """
    # Create user account
    user = User(
        email=registration.email,
        username=registration.username,
        first_name=registration.first_name,
        last_name=registration.last_name,
        hashed_password=get_password_hash(registration.password),
        is_active=True,
        is_alumni=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create alumni profile
    alumni = Alumni(
        user_id=user.id,
        phone=registration.phone,
        date_of_birth=registration.date_of_birth,
        gender=registration.gender,
        address=registration.address,
        city=registration.city,
        state=registration.state,
        country=registration.country,
        postal_code=registration.postal_code,
        bio=registration.bio,
        linkedin_url=str(registration.linkedin_url) if registration.linkedin_url else None,
        is_active=True,
        is_verified=False  # Alumni need verification by college admin
    )
    db.add(alumni)
    db.commit()
    db.refresh(alumni)
    
    return alumni

def bulk_preregister_alumni(db: Session, *, alumni_data: list) -> Dict[str, int]:
    """
    Preregister multiple alumni from a list of dictionaries
    Returns counts of created and updated records
    """
    created_count = 0
    updated_count = 0
    
    for data in alumni_data:
        email = data.get("email")
        if not email:
            continue
            
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create a new user with temporary password
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            temp_password = f"temp_{email.split('@')[0]}"
            
            user = User(
                email=email,
                username=email.split('@')[0],
                first_name=first_name,
                last_name=last_name,
                hashed_password=get_password_hash(temp_password),
                is_active=True,
                is_alumni=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create alumni profile
            alumni = Alumni(
                user_id=user.id,
                is_active=True,
                is_verified=True  # Preregistered alumni are verified by default
            )
            db.add(alumni)
            db.commit()
            db.refresh(alumni)
            
            created_count += 1
        else:
            # Get or create alumni profile
            alumni = db.query(Alumni).filter(Alumni.user_id == user.id).first()
            if not alumni:
                alumni = Alumni(
                    user_id=user.id,
                    is_active=True,
                    is_verified=True
                )
                db.add(alumni)
                db.commit()
                db.refresh(alumni)
                created_count += 1
            else:
                updated_count += 1
        
        # Create education record if department, degree and batch years provided
        if all(key in data for key in ["department", "degree", "batch_year_start", "batch_year_end"]):
            # Get or create department
            dept_name = data.get("department")
            department = db.query(Department).filter(Department.name == dept_name).first()
            if not department:
                department = Department(name=dept_name)
                db.add(department)
                db.commit()
                db.refresh(department)
            
            # Check if education record exists
            education = db.query(Education).filter(
                Education.alumni_id == alumni.id,
                Education.degree == data.get("degree"),
                Education.batch_year_end == int(data.get("batch_year_end"))
            ).first()
            
            if not education:
                education = Education(
                    alumni_id=alumni.id,
                    department_id=department.id,
                    degree=data.get("degree"),
                    batch_year_start=int(data.get("batch_year_start")),
                    batch_year_end=int(data.get("batch_year_end")),
                    major=data.get("major", ""),
                    gpa=float(data.get("gpa")) if data.get("gpa") else None
                )
                db.add(education)
                db.commit()
    
    return {"created": created_count, "updated": updated_count}


def preregister_alumni_from_csv(db: Session, *, csv_file_path: str) -> Dict[str, int]:
    """
    Read alumni data from a CSV file and preregister them
    """
    alumni_data = []
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            alumni_data.append(row)
    
    return bulk_preregister_alumni(db=db, alumni_data=alumni_data)