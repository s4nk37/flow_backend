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
from app.schemas.todos_schema import TodosSchema

api_router = APIRouter(tags=["Todos"])


# Retrieve all todos with pagination and filtering
@api_router.get("/todos", response_model=TodosSchema)
def read_todos(
    skip: int = 0,
    limit: int = 20,
    is_completed: Optional[bool] = None,
    priority: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    query = db.query(TodoModel).filter(TodoModel.user_id == current_user.id)

    if is_completed is not None:
        query = query.filter(TodoModel.is_completed == is_completed)
    
    if priority is not None:
        query = query.filter(TodoModel.priority == priority)

    todos_list = query.offset(skip).limit(limit).all()

    return TodosSchema(
        todos=todos_list, updatedAt=int(datetime.now(timezone.utc).timestamp())
    )


# Retrieve a single todo
@api_router.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id, TodoModel.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


# Create a new todo
@api_router.post("/todos", response_model=TodoResponse)
def create_todo(
    payload: TodoCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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

    return new_todo

@api_router.post("/todos/bulk", response_model=BulkTodoResponse)
def bulk_create_todos(
    payload: BulkTodoCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    created = []
    failed = []
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
            db.flush()
            created.append(new_todo)
        except Exception as e:
            db.rollback()
            failed.append({"index": idx, "error": str(e)})
    db.commit()
    for todo in created:
        db.refresh(todo)
    return BulkTodoResponse(created=created, failed=failed)



# Update an existing todo
@api_router.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: str,
    payload: TodoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id, TodoModel.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    todo.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(todo)

    return todo


# Delete a todo
@api_router.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(
    todo_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id, TodoModel.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully"}


# Delete All Todos (For Testing Purposes)
@api_router.delete("/todos", response_model=dict)
def delete_all_todos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db.query(TodoModel).filter(TodoModel.user_id == current_user.id).delete()
    db.commit()
    return {"message": "All todos deleted successfully"}
