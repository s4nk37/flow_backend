from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.refresh_token_model import RefreshTokenModel
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.database.session import get_db
from app.core.security import (
    create_refresh_token,
    get_current_user,
    verify_password,
    create_access_token,
)
from app.database.user_crud import create_user, get_user_by_email
from app.utils.timezone_helper import make_aware
from app.utils.logger import logger

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, payload.email)

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, payload.email, payload.password)
    return user


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db), request: Request = None):
    user = get_user_by_email(db, payload.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token()

    # Save refresh token in DB
    db_token = RefreshTokenModel(
        user_id=user.id,
        token=refresh_token,
        user_agent=request.headers.get("User-Agent"),
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_tokens(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    logger.info(f"Refresh token received: {refresh_token}")  # Debugging line

    db_token = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token == refresh_token)
        .first()
    )

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db_token.expires_at = make_aware(db_token.expires_at)

    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # issue new tokens
    new_access = create_access_token({"sub": str(db_token.user_id)})
    new_refresh = create_refresh_token()

    # delete old refresh
    db.delete(db_token)
    db.commit()

    # store new refresh
    new_db_token = RefreshTokenModel(user_id=db_token.user_id, token=new_refresh)
    db.add(new_db_token)
    db.commit()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    db_token = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token == refresh_token)
        .first()
    )
    if db_token:
        db.delete(db_token)
        db.commit()

    return {"message": "Logged out from this device"}


@router.post("/logout-all")
def logout_all(
    user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user.id).delete()
    db.commit()
    return {"message": "Logged out from all devices"}
