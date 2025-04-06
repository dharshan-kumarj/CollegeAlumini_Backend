from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File, Query, Path, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from config.main import oauth2_scheme, decode_jwt_token
from services.main import AuthService, AlumniService, AdminService
import os

app = FastAPI(title="College Alumni System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return payload

# Alumni-only access
async def alumni_only(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_alumni", False):
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# Admin-only access
async def admin_only(current_user: dict = Depends(get_current_user)):
    if current_user.get("is_alumni", True):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ------------------------------ AUTH ROUTES ------------------------------
@app.post("/api/auth/register")
async def register(user_data: dict = Body(...)):
    result = AuthService.register_user(user_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    result = AuthService.login_user(form_data.username, form_data.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

# ------------------------------ ALUMNI ROUTES ------------------------------
@app.get("/api/alumni/profile")
async def get_profile(current_user: dict = Depends(alumni_only)):
    alumni_id = current_user.get("alumni_id")
    if not alumni_id:
        raise HTTPException(status_code=404, detail="Alumni profile not found")
    
    result = AlumniService.get_alumni_profile(alumni_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/api/alumni/profile")
async def create_profile_entry(
    entry_data: dict = Body(...), 
    current_user: dict = Depends(alumni_only)
):
    alumni_id = current_user.get("alumni_id")
    if not alumni_id:
        raise HTTPException(status_code=404, detail="Alumni profile not found")
    
    result = AlumniService.create_profile_entry(alumni_id, entry_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.put("/api/alumni/profile")
async def update_profile(
    profile_data: dict = Body(...), 
    current_user: dict = Depends(alumni_only)
):
    alumni_id = current_user.get("alumni_id")
    if not alumni_id:
        raise HTTPException(status_code=404, detail="Alumni profile not found")
    
    result = AlumniService.update_alumni_profile(alumni_id, profile_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.delete("/api/alumni/profile/{type}/{id}")
async def delete_profile_item(
    type: str = Path(...),
    id: int = Path(...),
    current_user: dict = Depends(alumni_only)
):
    alumni_id = current_user.get("alumni_id")
    if not alumni_id:
        raise HTTPException(status_code=404, detail="Alumni profile not found")
    
    result = AlumniService.delete_profile_item(alumni_id, type, id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/alumni/profile/image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(alumni_only)
):
    # This is a placeholder for image upload functionality
    # In a real app, you would save the image and update the database
    return {"filename": file.filename, "status": "Image upload placeholder"}

# ------------------------------ ADMIN ROUTES ------------------------------
@app.get("/api/admin/alumni")
async def get_all_alumni(
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0, le=100),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.get_all_alumni(page, per_page)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# @app.get("/api/admin/alumni/{id}")
# async def get_alumni_by_id(
#     id: int = Path(...),
#     current_user: dict = Depends(admin_only)
# ):
#     result = AdminService.get_alumni_by_id(id)
#     if "error" in result:
#         raise HTTPException(status_code=404, detail=result["error"])
#     return result

@app.put("/api/admin/alumni/{id}")
async def update_alumni(
    id: int = Path(...),
    profile_data: dict = Body(...),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.update_alumni_by_admin(id, profile_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/admin/alumni/{alumni_id}/job")
async def add_job_for_alumni(
    alumni_id: int = Path(...),
    job_data: dict = Body(...),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.add_job_for_alumni(alumni_id, job_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.delete("/api/admin/alumni/{alumni_id}/job/{job_id}")
async def delete_job_for_alumni(
    alumni_id: int = Path(...),
    job_id: int = Path(...),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.delete_job_for_alumni(alumni_id, job_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/admin/alumni/{alumni_id}/education")
async def add_education_for_alumni(
    alumni_id: int = Path(...),
    education_data: dict = Body(...),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.add_education_for_alumni(alumni_id, education_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.delete("/api/admin/alumni/{alumni_id}/education/{education_id}")
async def delete_education_for_alumni(
    alumni_id: int = Path(...),
    education_id: int = Path(...),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.delete_education_for_alumni(alumni_id, education_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# First define the specific route
@app.get("/api/admin/alumni/filter")
async def filter_alumni(
    department: Optional[str] = None,
    end_year: Optional[int] = None,
    start_year: Optional[int] = None,
    cgpa: Optional[float] = None,
    degree: Optional[str] = None,
    full_name: Optional[str] = None,
    location: Optional[str] = None,
    company_name: Optional[str] = None,
    position: Optional[str] = None,
    availability_for_mentorship: Optional[bool] = None,
    current_user: dict = Depends(admin_only)
):
    filters = {}
    if department:
        filters["department"] = department
    if end_year:
        filters["end_year"] = end_year
    if start_year:
        filters["start_year"] = start_year
    if cgpa:
        filters["cgpa"] = cgpa
    if degree:
        filters["degree"] = degree
    if full_name:
        filters["full_name"] = full_name
    if location:
        filters["location"] = location
    if company_name:
        filters["company_name"] = company_name
    if position:
        filters["position"] = position
    if availability_for_mentorship is not None:
        filters["availability_for_mentorship"] = availability_for_mentorship
    
    result = AdminService.filter_alumni(filters)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# Then define the route with path parameter
@app.get("/api/admin/alumni/{id}")
async def get_alumni_by_id(
    id: int = Path(...),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.get_alumni_by_id(id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/api/admin/filter-categories")
async def get_filter_categories(current_user: dict = Depends(admin_only)):
    result = AdminService.get_filter_categories()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.delete("/api/admin/alumni/{id}")
async def delete_alumni(
    id: int = Path(...),
    current_user: dict = Depends(admin_only)
):
    result = AdminService.delete_alumni(id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# For running the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
