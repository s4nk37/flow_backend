from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    isCompleted: bool = False

class TodoCreate(TodoBase):
    pass

class TodoResponse(TodoBase):
    id: str
    createdAt: datetime
    updatedAt: Optional[datetime]
    completedAt: Optional[datetime]
    reminderAt: Optional[datetime]

    class Config:
        orm_mode = True
