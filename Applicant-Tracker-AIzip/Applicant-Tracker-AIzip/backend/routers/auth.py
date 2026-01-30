from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database.models import User
from backend.core.security import hash_password, verify_password, create_access_token

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str


class MessageResponse(BaseModel):
    message: str


@router.post("/signup", response_model=MessageResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Normalize role
    request.role = request.role.strip().lower()

    if request.role not in ["candidate", "recruiter"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'candidate' or 'recruiter'"
        )
    
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = hash_password(request.password)
    
    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        role=request.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }
