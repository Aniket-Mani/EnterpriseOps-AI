
import json
from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session

from app.db.models.agent_run import (
    AgentRun,
    AgentType,
    AgentRunStatus,
)
from app.db.models.agent_message import AgentMessage, MessageType
from app.db.models.audit_log import AuditLog, ActorType


def utcnow():
    return datetime.now(timezone.utc)


def persist_agent_execution(
    session: Session,
    *,
    task_id: UUID,
    agent: str,
    input_data: dict,
    output_data: dict | None = None,
    error: str | None = None,
    started_at: datetime | None = None,
) -> AgentRun:

    now = utcnow()
    agent_type = AgentType(agent)

    output_data = output_data or {}

    run = AgentRun(
        task_id=task_id,
        agent_type=agent_type,
        status=(
            AgentRunStatus.FAILED
            if error
            else AgentRunStatus.COMPLETED
        ),
        input_data=input_data,
        output_data=output_data,
        error_message=error[:2000] if error else None,
        started_at=started_at or now,
        completed_at=now,
    )

    session.add(run)
    session.flush()

    message = AgentMessage(
        task_id=task_id,
        agent_run_id=run.id,
        sender=agent_type,
        message_type=(
            MessageType.ERROR if error else MessageType.RESULT
        ),
        subject=f"{agent.title()} execution",
        content=(
            error
            if error
            else f"{agent.title()} execution completed."
        ),
        payload={
            "input": input_data,
            "output": output_data,
            "error": error,
            "run_id": str(run.id),
        },
        correlation_id=task_id,
    )

    session.add(message)

    session.add(
        AuditLog(
            task_id=task_id,
            actor_type=ActorType.AGENT,
            action=(
                "agent_execution_failed"
                if error
                else "agent_execution_completed"
            ),
            entity_type="agent_run",
            entity_id=run.id,
            description=(
                f"{agent.title()} execution failed: {error}"
                if error
                else f"{agent.title()} execution completed."
            ),
            metadata_json={
                "agent": agent,
                "run_id": str(run.id),
                "status": run.status.value,
            },
        )
    )

    session.flush()

    return run
