from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import time

from app.database import SessionLocal
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoResponse
from app.schemas.todos_response import TodosResponse

router = APIRouter(prefix="/todos", tags=["Todos"])

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# CREATE TODO
# ---------------------------
@router.post("/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        createdAt=datetime.utcnow(),
        isCompleted=todo.isCompleted,
        updatedAt=None,
        completedAt=None,
        reminderAt=None,
    )

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo


# ---------------------------
# GET ALL TODOS (UPDATED FORMAT)
# ---------------------------
@router.get("/", response_model=TodosResponse)
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()

    updated_at_ms = int(time.time() * 1000)  # millisecond timestamp

    return {
        "todos": todos,
        "updatedAt": updated_at_ms
    }


# ---------------------------
# GET SINGLE TODO
# ---------------------------
@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.id == todo_id).first()


# ---------------------------
# UPDATE TODO
# ---------------------------
@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.isCompleted = todo.isCompleted
    db_todo.updatedAt = datetime.utcnow()

    # if completed, set completedAt time
    if todo.isCompleted:
        db_todo.completedAt = datetime.utcnow()

    db.commit()
    db.refresh(db_todo)
    return db_todo


# ---------------------------
# DELETE TODO
# ---------------------------
@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    db.delete(db_todo)
    db.commit()

    return {"message": "Todo deleted"}
