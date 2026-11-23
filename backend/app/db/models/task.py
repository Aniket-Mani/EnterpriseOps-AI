import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

def utc_now():
    return datetime.now(timezone.utc)

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED= "cancelled"

class OperationalTask(SQLModel, table = True):
    __tablename__ = "operational_tasks"

    id:uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    task_key: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False)
    )

    user_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id"), nullable=False, index=True)
    )

    objective: str = Field(nullable=False,)

    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        sa_column=Column(SAEnum(TaskStatus,name="task_status",values_callable=lambda enum: [e.value for e in enum],),nullable=False),
    )

    priority: str = Field(
        default="normal", max_length=20, nullable=False
    )

    input_context: dict = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False),
    )

    final_report: dict| None = Field(
        default=None, sa_column=Column(JSONB, nullable=True),
    )

    created_at: datetime = Field(
            default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable = False),
        )
        
    updated_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable = False),
    )

    completed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable = True),
    )




