import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.db.models.agent_run import AgentType

def utc_now():
    return datetime.now(timezone.utc)

class MessageType(str, Enum):
    TASK_ASSIGNMENT = "task_assignment"
    STATUS_UPDATE = "status_update"
    INFORMATION_REQUEST = "information_request"
    INFORMATION_RESPONSE = "information_response"
    RESULT = "result"
    ERROR = "error"
    HANDOFF = "handoff"

class AgentMessage(SQLModel, table = True):
    __tablename__="agent_messages"

    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    task_id:uuid.UUID = Field(
        sa_column=Column(ForeignKey("operational_tasks.id"), nullable=False, index=True,)
    )

    agent_run_id:uuid.UUID = Field(
        default=None,
        sa_column=Column(ForeignKey("agent_runs.id"), nullable=True, index= True,),
    )

    sender: AgentType = Field(
        sa_column=Column(SAEnum(AgentType,name="agent_type",values_callable=lambda enum: [e.value for e in enum],), nullable=False,)
    )

    recipient: AgentType = Field(
        default=None,
        sa_column=Column(SAEnum(AgentType,name="agent_type",values_callable=lambda enum: [e.value for e in enum],), nullable=True,),
    )

    message_type: MessageType = Field(
        sa_column=Column(SAEnum(MessageType,name="message_type",values_callable=lambda enum:[e.value for e in enum],), nullable=False,)
    )

    subject: str = Field(max_length=255, nullable=False,)

    content: str = Field(sa_column=Column(Text, nullable=False))

    payload: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )

    correlation_id:uuid.UUID | None = Field(default=None)

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True),nullable=False),
    )






