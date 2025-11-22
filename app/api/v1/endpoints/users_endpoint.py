from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.user_schema import UserResponse
from app.models.user_model import UserModel
from app.models.todo_model import TodoModel
from app.models.refresh_token_model import RefreshTokenModel
from app.database.session import get_db

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.delete("/me")
def delete_account(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete the current user's account and all associated data."""
    # Delete all todos
    db.query(TodoModel).filter(TodoModel.user_id == current_user.id).delete()
    
    # Delete all refresh tokens
    db.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == current_user.id).delete()
    
    # Delete the user
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}
