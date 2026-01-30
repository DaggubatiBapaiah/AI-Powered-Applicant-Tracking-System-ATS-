from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from backend.database.db import get_db
from backend.database.models import Resume, JobDescription, MatchResult, User
from backend.services.matching_engine import match_resume_to_job
from backend.core.security import require_role

router = APIRouter()

class MatchRequest(BaseModel):
    resume_id: int
    job_id: int

class MatchResponse(BaseModel):
    score: float
    missing_keywords: List[str]

class MatchHistoryResponse(BaseModel):
    id: int
    job_id: int
    score: float
    missing_keywords: str
    created_at: datetime

    class Config:
        from_attributes = True

class MatchInsightResponse(BaseModel):
    candidate_email: str
    score: float
    missing_keywords: str

@router.get("/me", response_model=List[MatchHistoryResponse])
def get_my_match_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    results = db.query(MatchResult).join(Resume).filter(
        Resume.user_id == current_user.id
    ).all()
    return results

@router.get("/job/{job_id}", response_model=List[MatchInsightResponse])
def get_job_match_insights(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    # Verify job belongs to recruiter
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied or job not found"
        )
    
    # Fetch matches for this job
    results = db.query(
        User.email.label("candidate_email"),
        MatchResult.score,
        MatchResult.missing_keywords
    ).join(Resume, MatchResult.resume_id == Resume.id)\
     .join(User, Resume.user_id == User.id)\
     .filter(MatchResult.job_id == job_id).all()
    
    return results

@router.post("/", response_model=MatchResponse)
def perform_match(
    request: MatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    # Fetch resume and ensure it belongs to the current user
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied"
        )
    
    # Fetch job description
    job = db.query(JobDescription).filter(JobDescription.id == request.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    # Perform matching
    result = match_resume_to_job(str(resume.content), str(job.description))
    
    # Store result in DB
    match_result = MatchResult(
        resume_id=resume.id,
        job_id=job.id,
        score=result["score"],
        missing_keywords=", ".join(result["missing_keywords"])
    )
    db.add(match_result)
    db.commit()
    db.refresh(match_result)
    
    return {
        "score": match_result.score,
        "missing_keywords": result["missing_keywords"]
    }
