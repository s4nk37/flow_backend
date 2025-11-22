from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = Field(default=False, alias="isCompleted")
    priority: int = Field(default=0, ge=0, le=3, description="0=None, 1=Low, 2=Medium, 3=High")
    reminder_at: Optional[datetime] = Field(default=None, alias="reminderAt")
    is_deleted: bool = Field(default=False, alias="isDeleted")
    is_synced: bool = Field(default=False, alias="isSynced")


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = Field(default=None, alias="isCompleted")
    priority: Optional[int] = Field(default=None, ge=0, le=3)
    reminder_at: Optional[datetime] = Field(default=None, alias="reminderAt")
    is_deleted: Optional[bool] = Field(default=None, alias="isDeleted")
    is_synced: Optional[bool] = Field(default=None, alias="isSynced")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")


class TodoResponse(TodoBase):
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(alias="updatedAt")
    completed_at: Optional[datetime] = Field(alias="completedAt")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class BulkTodoCreate(BaseModel):
    todos: List[TodoCreate]


class BulkTodoResponse(BaseModel):
    created: List[TodoResponse]
    failed: List[dict]  # List of {index: int, error: str}
