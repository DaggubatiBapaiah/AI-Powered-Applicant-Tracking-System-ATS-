from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Routers (adjust imports if your paths differ)
from backend.routers import auth, resumes, jobs, match, applications

app = FastAPI(title="AI Applicant Tracking System")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# STATIC FRONTEND
# -----------------------------
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("frontend/index.html")

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/info")
def info():
    return {
        "app": "AI ATS",
        "frontend": "enabled",
        "backend": "FastAPI",
    }

# -----------------------------
# API ROUTERS (uncomment if present)
# -----------------------------
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(match.router, prefix="/match", tags=["Matching"])
app.include_router(applications.router, prefix="/applications", tags=["Applications"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
