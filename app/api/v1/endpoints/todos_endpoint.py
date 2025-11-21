from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.todo_model import TodoModel
from app.schemas.todo_schema import TodoSchema
from app.schemas.todos_schema import TodosSchema

api_router = APIRouter(tags=["Todos"])


# Retrieve all todos
@api_router.get("/todos", response_model=TodosSchema)
def read_todos(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    todos_list = db.query(TodoModel).filter(TodoModel.user_id == current_user).all()

    return TodosSchema(
        todos=todos_list, updatedAt=int(datetime.now(timezone.utc).timestamp())
    )


# Create a new todo
@api_router.post("/todos", response_model=TodoSchema)
def create_todo(
    payload: TodoSchema,
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_todo = TodoModel(
        title=payload.title,
        description=payload.description,
        reminder_at=payload.reminder_at,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_completed=False,
        is_deleted=False,
        is_synced=False,
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


# Update an existing todo
@api_router.put("/todos/{todo_id}", response_model=TodoSchema)
def update_todo(
    todo_id: int,
    payload: TodoSchema,
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": "Todo not found"}

    todo.title = payload.title
    todo.description = payload.description
    todo.is_completed = payload.is_completed
    todo.updated_at = datetime.now(timezone.utc)
    todo.completed_at = payload.completed_at
    todo.reminder_at = payload.reminder_at
    todo.is_deleted = payload.is_deleted
    todo.is_synced = payload.is_synced

    db.commit()
    db.refresh(todo)

    return todo


# Delete a todo
@api_router.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(
    todo_id: int,
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": "Todo not found"}

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully"}


# Delete All Todos (For Testing Purposes)
@api_router.delete("/todos", response_model=dict)
def delete_all_todos(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    db.query(TodoModel).delete()
    db.commit()
    return {"message": "All todos deleted successfully"}
