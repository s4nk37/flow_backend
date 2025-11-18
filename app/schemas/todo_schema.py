from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TodoSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = Field(alias="isCompleted")
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(alias="updatedAt")
    completed_at: Optional[datetime] = Field(alias="completedAt")
    reminder_at: Optional[datetime] = Field(alias="reminderAt")
    is_deleted: bool = Field(alias="isDeleted")
    is_synced: bool = Field(alias="isSynced")

    model_config = {
        "from_attributes": True,  # NEW in Pydantic 2 (replaces orm_mode)
        "populate_by_name": True,  # allow using python field names for input
    }
