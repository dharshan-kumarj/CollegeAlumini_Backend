from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Alumni Database API",
    description="API for College Alumni Database System",
    version="1.0.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS] + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files (for uploaded images)
os.makedirs("app/media/alumni_profiles", exist_ok=True)
app.mount("/media", StaticFiles(directory="app/media"), name="media")

@app.get("/")
def root():
    return {"message": "Welcome to the College Alumni Database API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Global exception handler for HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)