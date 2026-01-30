from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.db import get_db
from backend.database.models import JobDescription, User
from backend.database.schemas import JobDescriptionCreate, JobDescriptionResponse
from backend.core.security import require_role

router = APIRouter()

@router.post("/", response_model=JobDescriptionResponse)
def create_job(
    job_in: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    new_job = JobDescription(
        recruiter_id=current_user.id,
        title=job_in.title,
        description=job_in.description
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/me", response_model=List[JobDescriptionResponse])
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    jobs = db.query(JobDescription).filter(JobDescription.recruiter_id == current_user.id).all()
    return jobs

@router.get("/", response_model=List[JobDescriptionResponse])
def get_all_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    jobs = db.query(JobDescription).all()
    return jobs
