from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.refresh_token_model import RefreshTokenModel
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, EmailCheck
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
from app.utils.response import (
    success_response,
    unauthorized_response,
    conflict_response,
    ErrorCode
)

router = APIRouter()


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    try:
        existing = get_user_by_email(db, payload.email)

        if existing:
            return conflict_response(
                message="Email already registered",
                details={"email": payload.email}
            )

        user = create_user(db, payload.email, payload.password, payload.name)
        
        return success_response(
            data=UserResponse.model_validate(user),
            message="User registered successfully",
            status_code=201
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}", exc_info=True)
        raise


@router.post("/check-email")
def check_email(payload: EmailCheck, db: Session = Depends(get_db)):
    """
    Check if an email is already registered.
    """
    try:
        existing = get_user_by_email(db, payload.email)
        return success_response(
            data={"exists": bool(existing)},
            message="Email check completed"
        )
    except Exception as e:
        db.rollback()
        raise


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db), request: Request = None):
    """
    Login and receive access and refresh tokens.
    """
    try:
        user = get_user_by_email(db, payload.email)

        if not user:
            return unauthorized_response(
                message="Invalid email or password",
                error_code=ErrorCode.INVALID_CREDENTIALS
            )

        if not verify_password(payload.password, user.hashed_password):
            return unauthorized_response(
                message="Invalid email or password",
                error_code=ErrorCode.INVALID_CREDENTIALS
            )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token()

        # Save refresh token in DB
        db_token = RefreshTokenModel(
            user_id=user.id,
            token=refresh_token,
            user_agent=request.headers.get("User-Agent") if request else None,
        )
        db.add(db_token)
        db.commit()

        return success_response(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": UserResponse.model_validate(user)
            },
            message="Login successful"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Login error: {e}", exc_info=True)
        raise


@router.post("/refresh")
def refresh_tokens(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    try:
        logger.info(f"Refresh token received: {refresh_token}")

        db_token = (
            db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.token == refresh_token)
            .first()
        )

        if not db_token:
            return unauthorized_response(
                message="Invalid refresh token",
                error_code=ErrorCode.INVALID_TOKEN
            )

        db_token.expires_at = make_aware(db_token.expires_at)

        if db_token.expires_at < datetime.now(timezone.utc):
            # Delete expired token
            db.delete(db_token)
            db.commit()
            return unauthorized_response(
                message="Refresh token expired",
                error_code=ErrorCode.TOKEN_EXPIRED
            )

        # Issue new tokens
        new_access = create_access_token({"sub": str(db_token.user_id)})
        new_refresh = create_refresh_token()

        # Delete old refresh token
        db.delete(db_token)
        db.commit()

        # Store new refresh token
        new_db_token = RefreshTokenModel(
            user_id=db_token.user_id,
            token=new_refresh,
            user_agent=db_token.user_agent
        )
        db.add(new_db_token)
        db.commit()

        return success_response(
            data={
                "access_token": new_access,
                "refresh_token": new_refresh,
                "token_type": "bearer"
            },
            message="Tokens refreshed successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise


@router.post("/logout")
def logout(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    """
    Logout from current device by invalidating refresh token.
    """
    try:
        db_token = (
            db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.token == refresh_token)
            .first()
        )
        
        if db_token:
            db.delete(db_token)
            db.commit()
        
        return success_response(
            data={},
            message="Logged out from this device"
        )
    except Exception as e:
        db.rollback()
        raise


@router.post("/logout-all")
def logout_all(
    user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Logout from all devices by invalidating all refresh tokens.
    """
    try:
        count = db.query(RefreshTokenModel).filter(
            RefreshTokenModel.user_id == user.id
        ).delete()
        
        db.commit()
        
        return success_response(
            data={"devices_logged_out": count},
            message=f"Logged out from all devices ({count} devices)"
        )
    except Exception as e:
        db.rollback()
        raise
