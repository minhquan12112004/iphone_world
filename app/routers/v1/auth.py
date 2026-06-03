from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.schemas.auth_schemas import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_user,
    create_access_token,
    get_user_by_email,
    get_current_user,
)
from app.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = create_user(db, name=payload.name, email=payload.email, password=payload.password)
    return UserResponse.from_orm(user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def read_me(current_user=Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_orm(current_user)
