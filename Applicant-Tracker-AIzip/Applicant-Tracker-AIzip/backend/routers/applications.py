from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from backend.database.db import get_db
from backend.database.models import Application, User, JobDescription
from backend.database.schemas import ApplicationResponse, ApplicationUpdate
from backend.core.security import require_role

router = APIRouter()

class ApplicationCreateRequest(BaseModel):
    job_id: int

@router.post("/", response_model=ApplicationResponse)
def create_application(
    request: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    # Check if job exists
    job = db.query(JobDescription).filter(JobDescription.id == request.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Prevent duplicate applications
    existing_app = db.query(Application).filter(
        Application.job_id == request.job_id,
        Application.candidate_id == current_user.id
    ).first()
    
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    new_app = Application(
        job_id=request.job_id,
        candidate_id=current_user.id,
        status="pending"
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # --- Auto-Match Trigger ---
    # --- Auto-Match Trigger ---
    from backend.services.matching_engine import match_resume_to_job
    from backend.database.models import Resume, MatchResult
    
    # 1. Get Candidate Resume
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if resume:
        # 2. Calculate Match
        match_result = match_resume_to_job(resume.content, job.description)
        score = match_result["score"]
        missing = match_result["missing_keywords"]
        
        # 3. Store Match Result
        # Check if exists first to avoid dupes (optional based on logic, but safe)
        existing_match = db.query(MatchResult).filter(
            MatchResult.resume_id == resume.id,
            MatchResult.job_id == job.id
        ).first()

        if not existing_match:
            new_match = MatchResult(
                resume_id=resume.id,
                job_id=job.id,
                score=score,
                missing_keywords=", ".join(missing) # Convert list to string
            )
            db.add(new_match)
            db.commit()

    return new_app

from backend.database.schemas import ApplicationResponse, ApplicationUpdate, RecruiterApplicationResponse
from backend.database.models import Application, User, JobDescription, Resume, MatchResult

# ... (imports)

@router.get("/me", response_model=List[RecruiterApplicationResponse])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    apps = db.query(Application).filter(Application.candidate_id == current_user.id).all()
    results = []

    for app in apps:
        # Get match result
        resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
        score = None
        missing = None
        
        if resume:
            match = db.query(MatchResult).filter(MatchResult.resume_id == resume.id, MatchResult.job_id == app.job_id).first()
            if match:
                score = match.score
                missing = match.missing_keywords
        
        app_dict = {c.name: getattr(app, c.name) for c in app.__table__.columns}
        app_dict.update({
            "candidate_email": current_user.email,
            "match_score": score,
            "missing_skills": missing
        })
        results.append(app_dict)
        
    return results

@router.get("/job/{job_id}", response_model=List[RecruiterApplicationResponse])
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    # Verify the recruiter owns the job
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this job's applications"
        )
    
    apps = db.query(Application).filter(Application.job_id == job_id).all()
    results = []

    for app in apps:
        candidate = db.query(User).filter(User.id == app.candidate_id).first()
        resume = db.query(Resume).filter(Resume.user_id == app.candidate_id).first()
        
        score = None
        missing = None
        
        if resume:
            match = db.query(MatchResult).filter(MatchResult.resume_id == resume.id, MatchResult.job_id == job_id).first()
            if match:
                score = match.score
                missing = match.missing_keywords
        
        # Create a dict from the app object and update with new fields
        app_dict = {c.name: getattr(app, c.name) for c in app.__table__.columns}
        app_dict.update({
            "candidate_email": candidate.email if candidate else "Unknown",
            "match_score": score,
            "missing_skills": missing
        })
        results.append(app_dict)
        
    return results

@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    update_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    application = db.query(Application).join(JobDescription).filter(
        Application.id == application_id,
        JobDescription.recruiter_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or access denied"
        )
    
    valid_statuses = ["shortlisted", "rejected", "interview"]
    if update_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    application.status = update_data.status
    db.commit()
    db.refresh(application)
    return application
