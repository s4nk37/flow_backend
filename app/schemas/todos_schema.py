from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.todo_schema import TodoSchema
from datetime import datetime


class TodosSchema(BaseModel):
    todos: List[TodoSchema]
    pdated_at: Optional[datetime] = Field(alias="updatedAt")
    user_id: int

    model_config = {"from_attributes": True}
