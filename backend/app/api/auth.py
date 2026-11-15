from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import password_hash, credentials_error, get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas import Token, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    login_id = form.username.lower()
    user = db.query(User).filter(or_(User.email == login_id, User.username == login_id)).first()
    if user is None or not password_hash.verify(form.password, user.hashed_password):
        raise credentials_error()
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": str(user.id), "exp": expires}, JWT_SECRET, algorithm="HS256")
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user