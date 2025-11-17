from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.todo import TodoResponse

class TodosResponse(BaseModel):
    todos: List[TodoResponse]
    updatedAt: int

    class Config:
        orm_mode = True
