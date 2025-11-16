from fastapi import FastAPI
from app.database import engine, Base
from app.routes.todo import router as todo_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(todo_router)

@app.get("/")
def home():
    return {"message": "Flow Backend API is working 🚀"}
