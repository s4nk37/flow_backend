from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.user_schema import UserResponse
from app.models.user_model import UserModel
from app.models.todo_model import TodoModel
from app.models.refresh_token_model import RefreshTokenModel
from app.database.session import get_db
from app.utils.response import success_response

router = APIRouter()


@router.get("/me")
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    Get current user information.
    """
    return success_response(
        data=UserResponse.model_validate(current_user),
        message="User information retrieved successfully"
    )


@router.delete("/me")
def delete_account(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's account and all associated data.
    """
    try:
        user_id = current_user.id
        
        # Delete all todos (hard delete for account deletion)
        todos_count = db.query(TodoModel).filter(
            TodoModel.user_id == user_id
        ).delete()
        
        # Delete all refresh tokens
        tokens_count = db.query(RefreshTokenModel).filter(
            RefreshTokenModel.user_id == user_id
        ).delete()
        
        # Delete the user
        db.delete(current_user)
        db.commit()
        
        return success_response(
            data={
                "user_id": user_id,
                "todos_deleted": todos_count,
                "tokens_deleted": tokens_count
            },
            message="Account deleted successfully"
        )
    except Exception as e:
        db.rollback()
        raise
