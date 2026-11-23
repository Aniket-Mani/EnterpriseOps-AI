
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

def utc_now():
    return datetime.now(timezone.utc)

class ActorType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class AuditLog(SQLModel, table = True):
    __tablename__="audit_logs"

    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True,)

    task_id:uuid.UUID | None = Field(
        default=None,
        sa_column=Column(ForeignKey("operational_tasks.id"),nullable=True,index=True,),
    )

    actor_type: ActorType = Field(
        sa_column=Column(SAEnum(ActorType,name="actor_type",values_callable=lambda enum:[e.value for e in enum],), nullable=False,)
    )

    actor_id:uuid.UUID | None = Field(default=None)
    action: str = Field(sa_column=Column(String(150), nullable=False))

    entity_type: str = Field(sa_column=Column(String(100), nullable=False))
    entity_id:uuid.UUID | None = Field(default=None)

    description: str = Field(sa_column=Column(Text, nullable=False))

    metadata_json:dict= Field(
        default_factory=dict,
        sa_column=Column(JSONB,nullable=False),
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


