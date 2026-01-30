from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: str
    role: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeBase(BaseModel):
    content: str


class ResumeCreate(ResumeBase):
    pass


class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobDescriptionBase(BaseModel):
    title: str
    description: str


class JobDescriptionCreate(JobDescriptionBase):
    pass


class JobDescriptionResponse(JobDescriptionBase):
    id: int
    recruiter_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    job_id: int
    candidate_id: int


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RecruiterApplicationResponse(ApplicationResponse):
    candidate_email: str
    match_score: Optional[float] = None
    missing_skills: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: str


class MatchResultBase(BaseModel):
    resume_id: int
    job_id: int
    score: float
    missing_keywords: Optional[str] = None


class MatchResultCreate(MatchResultBase):
    pass


class MatchResultResponse(MatchResultBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
