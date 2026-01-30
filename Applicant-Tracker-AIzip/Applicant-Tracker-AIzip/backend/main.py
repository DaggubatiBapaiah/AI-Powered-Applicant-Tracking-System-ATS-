from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.database.db import engine, Base
from backend.database import models
from backend.routers.auth import router as auth_router
from backend.routers.resumes import router as resumes_router
from backend.routers.jobs import router as jobs_router
from backend.routers.match import router as match_router
from backend.routers.applications import router as applications_router

app = FastAPI(title="AI ATS Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"status": "AI ATS backend running"}


@app.get("/health", tags=["System"])
def health_check():
    """
    Returns the system health status.
    """
    return {"status": "ok"}


@app.get("/info", tags=["System"])
def get_info():
    """
    Returns application information and enabled features.
    """
    return {
        "app_name": "AI ATS Platform",
        "version": "1.0.0",
        "features": [
            "User Authentication (JWT)",
            "Resume Ingestion",
            "Job Description Management",
            "AI-Powered Keyword Matching",
            "Application Tracking Workflow"
        ]
    }


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
app.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
app.include_router(match_router, prefix="/match", tags=["Matching"])
app.include_router(applications_router, prefix="/applications", tags=["Applications"])
