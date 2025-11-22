from typing import Optional, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.todo_model import TodoModel
from app.models.user_model import UserModel
from app.schemas.todo_schema import TodoCreate, TodoUpdate, TodoResponse, BulkTodoCreate, BulkTodoResponse
from app.utils.response import (
    success_response,
    not_found_response,
    ErrorCode
)

api_router = APIRouter(tags=["Todos"])


# Retrieve all todos with pagination and filtering
@api_router.get("/todos")
def read_todos(
    cursor: Optional[int] = Query(None, description="Cursor for pagination (timestamp)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    completed: Optional[bool] = Query(None, alias="is_completed", description="Filter by completion status"),
    priority: Optional[int] = Query(None, ge=0, le=3, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    List todos with cursor-based pagination and filtering.
    """
    try:
        query = db.query(TodoModel).filter(
            TodoModel.user_id == current_user.id,
            TodoModel.is_deleted == False  # Filter out soft-deleted todos
        )

        if completed is not None:
            query = query.filter(TodoModel.is_completed == completed)
        
        if priority is not None:
            query = query.filter(TodoModel.priority == priority)
        
        # Cursor-based pagination using updated_at timestamp
        if cursor:
            cursor_dt = datetime.fromtimestamp(cursor, tz=timezone.utc)
            query = query.filter(TodoModel.updated_at < cursor_dt)
        
        # Order by updated_at descending for cursor pagination
        query = query.order_by(TodoModel.updated_at.desc())
        
        # Get one extra to check if there are more
        todos_list = query.limit(limit + 1).all()
        
        has_more = len(todos_list) > limit
        if has_more:
            todos_list = todos_list[:limit]
        
        # Get next cursor (timestamp of last item's updated_at)
        next_cursor = None
        if has_more and todos_list:
            next_cursor = int(todos_list[-1].updated_at.timestamp())
        
        # Convert to response models
        todos_data = [TodoResponse.model_validate(todo) for todo in todos_list]
        
        meta = {
            "pagination": {
                "next_cursor": next_cursor,
                "has_more": has_more
            } if next_cursor else None
        }
        
        return success_response(
            data=todos_data,
            meta=meta
        )
    except Exception as e:
        db.rollback()
        raise


# Retrieve a single todo
@api_router.get("/todos/{todo_id}")
def read_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get a single todo by ID.
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(todo_id)
        except ValueError:
            return not_found_response(
                message="Invalid todo ID format",
                error_code=ErrorCode.VALIDATION_ERROR
            )
        
        todo = db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.user_id == current_user.id,
            TodoModel.is_deleted == False
        ).first()
        
        if not todo:
            return not_found_response(
                message="Todo not found",
                error_code=ErrorCode.TODO_NOT_FOUND,
                details={"todo_id": todo_id}
            )
        
        return success_response(
            data=TodoResponse.model_validate(todo)
        )
    except Exception as e:
        db.rollback()
        raise


# Create a new todo
@api_router.post("/todos")
def create_todo(
    payload: TodoCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new todo.
    """
    try:
        new_todo = TodoModel(
            id=str(uuid.uuid4()),
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            reminder_at=payload.reminder_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_completed=payload.is_completed,
            is_deleted=payload.is_deleted,
            is_synced=payload.is_synced,
            user_id=current_user.id,
        )

        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)

        return success_response(
            data=TodoResponse.model_validate(new_todo),
            message="Todo created successfully",
            status_code=201
        )
    except Exception as e:
        db.rollback()
        raise


@api_router.post("/todos/bulk/create")
def bulk_create_todos(
    payload: BulkTodoCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create multiple todos in a single transaction.
    """
    created = []
    failed = []
    
    try:
        for idx, todo_data in enumerate(payload.todos):
            try:
                new_todo = TodoModel(
                    id=str(uuid.uuid4()),
                    title=todo_data.title,
                    description=todo_data.description,
                    priority=todo_data.priority,
                    reminder_at=todo_data.reminder_at,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    is_completed=todo_data.is_completed,
                    is_deleted=todo_data.is_deleted,
                    is_synced=todo_data.is_synced,
                    user_id=current_user.id,
                )
                db.add(new_todo)
                created.append(new_todo)
            except Exception as e:
                failed.append({"index": idx, "error": str(e)})
        
        # Commit all successful creations in one transaction
        db.commit()
        
        # Refresh all created todos
        for todo in created:
            db.refresh(todo)
        
        created_data = [TodoResponse.model_validate(todo) for todo in created]
        
        return success_response(
            data={
                "created": created_data,
                "failed": failed,
                "created_count": len(created),
                "failed_count": len(failed)
            },
            message=f"Bulk create completed: {len(created)} created, {len(failed)} failed"
        )
    except Exception as e:
        db.rollback()
        raise


# Update an existing todo (full update)
@api_router.put("/todos/{todo_id}")
def update_todo(
    todo_id: str,
    payload: TodoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Full update of a todo.
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(todo_id)
        except ValueError:
            return not_found_response(
                message="Invalid todo ID format",
                error_code=ErrorCode.VALIDATION_ERROR
            )
        
        todo = db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.user_id == current_user.id,
            TodoModel.is_deleted == False
        ).first()
        
        if not todo:
            return not_found_response(
                message="Todo not found",
                error_code=ErrorCode.TODO_NOT_FOUND,
                details={"todo_id": todo_id}
            )

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)

        todo.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(todo)

        return success_response(
            data=TodoResponse.model_validate(todo),
            message="Todo updated successfully"
        )
    except Exception as e:
        db.rollback()
        raise


# Partial update (PATCH) - recommended for sync
@api_router.patch("/todos/{todo_id}")
def patch_todo(
    todo_id: str,
    payload: TodoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Partial update of a todo (recommended for sync operations).
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(todo_id)
        except ValueError:
            return not_found_response(
                message="Invalid todo ID format",
                error_code=ErrorCode.VALIDATION_ERROR
            )
        
        todo = db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.user_id == current_user.id,
            TodoModel.is_deleted == False
        ).first()
        
        if not todo:
            return not_found_response(
                message="Todo not found",
                error_code=ErrorCode.TODO_NOT_FOUND,
                details={"todo_id": todo_id}
            )

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)

        todo.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(todo)

        return success_response(
            data=TodoResponse.model_validate(todo),
            message="Todo updated successfully"
        )
    except Exception as e:
        db.rollback()
        raise


# Delete a todo (soft delete)
@api_router.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft delete a todo (sets deleted=true).
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(todo_id)
        except ValueError:
            return not_found_response(
                message="Invalid todo ID format",
                error_code=ErrorCode.VALIDATION_ERROR
            )
        
        todo = db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.user_id == current_user.id,
            TodoModel.is_deleted == False
        ).first()
        
        if not todo:
            return not_found_response(
                message="Todo not found",
                error_code=ErrorCode.TODO_NOT_FOUND,
                details={"todo_id": todo_id}
            )

        # Soft delete
        todo.is_deleted = True
        todo.updated_at = datetime.now(timezone.utc)
        
        db.commit()

        return success_response(
            data={"todo_id": todo_id},
            message="Todo deleted successfully"
        )
    except Exception as e:
        db.rollback()
        raise


# Delete All Todos (For Testing Purposes)
@api_router.delete("/todos")
def delete_all_todos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Delete all todos for the current user (for testing purposes).
    """
    try:
        count = db.query(TodoModel).filter(
            TodoModel.user_id == current_user.id,
            TodoModel.is_deleted == False
        ).update({"is_deleted": True, "updated_at": datetime.now(timezone.utc)})
        
        db.commit()
        
        return success_response(
            data={"deleted_count": count},
            message=f"All todos deleted successfully ({count} todos)"
        )
    except Exception as e:
        db.rollback()
        raise
