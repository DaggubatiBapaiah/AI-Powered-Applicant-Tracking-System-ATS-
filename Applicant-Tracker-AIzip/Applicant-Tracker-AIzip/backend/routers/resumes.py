from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database.db import get_db
from backend.database.models import Resume, User
from backend.database.schemas import ResumeCreate, ResumeResponse
from backend.core.security import get_current_user, require_role

router = APIRouter()

@router.post("/", response_model=ResumeResponse)
def create_resume(
    resume_in: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    # Check for existing resume
    existing_resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    
    if existing_resume:
        existing_resume.content = resume_in.content
        existing_resume.created_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_resume)
        return existing_resume

    new_resume = Resume(
        user_id=current_user.id,
        content=resume_in.content
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return new_resume

@router.get("/me", response_model=List[ResumeResponse])
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes
