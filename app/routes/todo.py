from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoResponse
from datetime import datetime

router = APIRouter(prefix="/todos", tags=["Todos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        createdAt=datetime.utcnow(),
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.get("/", response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.id == todo_id).first()


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.isCompleted = todo.isCompleted
    db_todo.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted"}
