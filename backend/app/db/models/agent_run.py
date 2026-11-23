import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

def utc_now():
    return datetime.now(timezone.utc)

class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_for_approval"
    CANCELLED = "cancelled"

class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    ORDER = "order"
    INVENTORY = "inventory"
    PROCUREMENT = "procurement"
    FULFILLMENT = "fulfillment"
    VERIFICATION = "verification"


class AgentRun(SQLModel, table = True):
    __tablename__= "agent_runs"

    id:uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    task_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("operational_tasks.id"), nullable=False, index=True)
    )

    agent_type: AgentType = Field(
        sa_column=Column(SAEnum(AgentType, name = "agent_type", values_callable = lambda enum: [e.value for e in enum],), nullable = False,)
    )

    status: AgentRunStatus = Field(
        default = AgentRunStatus.PENDING,
        sa_column=Column(SAEnum(AgentRunStatus,name="agent_run_status",values_callable = lambda enum: [e.value for e in enum],),nullable=False,),
    )

    input_data: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable= False),
    )

    output_data: dict | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable= True),
    )

    error_message: str | None = Field(
        default=None,
        sa_column=Column(String(2000), nullable=True)
    )

    started_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


