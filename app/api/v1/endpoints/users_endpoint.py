from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.user_schema import UserResponse
from app.models.user_model import UserModel

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
