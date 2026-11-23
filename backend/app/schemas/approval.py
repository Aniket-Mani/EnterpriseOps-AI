import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.approval import ApprovalStatus


class ApprovalDecision(BaseModel):
    decision: ApprovalStatus
    reviewer_comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    agent_run_id: uuid.UUID | None
    action_type: str
    description: str
    requested_action: dict
    status: ApprovalStatus
    requested_at: datetime
    reviewed_at: datetime | None
    reviewed_by: uuid.UUID | None
    reviewer_comment: str | None