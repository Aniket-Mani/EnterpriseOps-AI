import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

def utc_now():
    return datetime.now(timezone.utc)


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ApprovalRequest(SQLModel, table = True):
    __tablename__= "approval_requests"

    id:uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    task_id:uuid.UUID = Field(
        sa_column=Column(ForeignKey("operational_tasks.id"),nullable=False, index=True,)
    )

    agent_run_id:uuid.UUID | None = Field(
        default=None,
        sa_column=Column(ForeignKey("agent_runs.id"), nullable=True, index=True),
    )

    action_type: str = Field(
        sa_column=Column(String(100), nullable=False)
    )

    description: str = Field(
        sa_column=Column(Text, nullable= False)
    )

    requested_action: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )

    status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        sa_column=Column(SAEnum(ApprovalStatus,name="approval_status",values_callable=lambda enum:[e.value for e in enum],),nullable=False,),
    )

    requested_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    reviewed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    reviewed_by: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(ForeignKey("users.id"),nullable=True),
    )

    reviewer_comment: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )