from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.todo_schema import TodoResponse
from datetime import datetime


class TodosSchema(BaseModel):
    todos: List[TodoResponse]
    updated_at: Optional[int] = Field(alias="updatedAt")

    model_config = {"from_attributes": True}
