import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import Token, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hash = PasswordHash.recommended()


def jwt_settings():
    secret = os.environ.get("JWT_SECRET")
    if not secret or secret == "REPLACE_WITH_A_LONG_RANDOM_SECRET":
        raise RuntimeError("Set JWT_SECRET to a long random value")
    try:
        minutes = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    except ValueError as exc:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer") from exc
    if minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
    return secret, minutes


def credentials_error():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    secret, _ = jwt_settings()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError, TypeError):
        raise credentials_error()
    user = db.get(User, user_id)
    if user is None:
        raise credentials_error()
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    login_id = form.username.lower()
    user = db.query(User).filter(or_(User.email == login_id, User.username == login_id)).first()
    if user is None or not password_hash.verify(form.password, user.hashed_password):
        raise credentials_error()
    secret, minutes = jwt_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    token = jwt.encode({"sub": str(user.id), "exp": expires}, secret, algorithm="HS256")
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
