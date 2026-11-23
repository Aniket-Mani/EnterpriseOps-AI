import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel,ConfigDict, Field

from app.db.models.agent_run import AgentType
from app.db.models.agent_message import MessageType

def utc_now():
    return datetime.now(timezone.utc)

class AgentMessage(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:uuid.UUID=Field(default_factory=uuid.uuid4)
    task_id:uuid.UUID
    agent_run_id:uuid.UUID |None = None

    sender: AgentType
    recipient: AgentType | None = None

    message_type: MessageType
    subject: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

    payload:dict = Field(default_factory=dict)
    correlation_id: uuid.UUID | None = None

    created_at: datetime = Field(default_factory=utc_now)

class AgentResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    agent: AgentType
    task_id: uuid.UUID

    success: bool
    summary: str = Field(min_length=1)

    data: dict = Field(default_factory=dict)
    error: str | None = None

    completed_at: datetime = Field(default_factory=utc_now)

