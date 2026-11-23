from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.task import TaskStatus


class TaskCreate(BaseModel):
    objective: str = Field(min_length=10, max_length=2000)
    priority: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    input_context: dict = Field(default_factory=dict)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_key: str
    objective: str
    status: TaskStatus
    priority: str
    input_context: dict
    final_report: dict | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None