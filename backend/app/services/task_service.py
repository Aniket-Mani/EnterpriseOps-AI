import re
import uuid
from datetime import datetime, timezone

from sqlalchemy.engine import make_url
from sqlmodel import Session, select
from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.db.models import OperationalTask, TaskStatus, User
from app.schemas.task import TaskCreate
from app.agents.graph import build_graph


def utc_now():
    return datetime.now(timezone.utc)


def extract_order_number(objective: str, input_context: dict) -> str | None:
    """Find an order number in the supplied context or objective."""
    order_number = input_context.get("order_number")

    if isinstance(order_number, str) and order_number.strip():
        return order_number.strip()

    match = re.search(r"\bORD-\d+\b", objective, re.IGNORECASE)
    return match.group(0).upper() if match else None


def execute_task_workflow(task: OperationalTask) -> dict:
    """Run the existing read-only LangGraph workflow with PostgreSQL persistence."""

    database_url = make_url(settings.database_url)
    checkpoint_url = database_url.set(
        drivername="postgresql"
    ).render_as_string(hide_password=False)

    thread_id = str(task.id)

    initial_state = {
        "task_id": task.id,
        "objective": task.objective,
        "order_number": task.input_context["order_number"],
        "task_context": task.input_context,
        "task_status": "running",
        "messages": [],
        "agent_results": [],
        "errors": [],
        "audit_events": [],
    }

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    with PostgresSaver.from_conn_string(checkpoint_url) as checkpointer:
        checkpointer.setup()

        graph = build_graph(checkpointer=checkpointer)
        result = graph.invoke(initial_state, config=config)

    return result["final_report"]


def create_and_execute_task(
    session: Session,
    user_id: uuid.UUID,
    task_data: TaskCreate,
) -> OperationalTask:
    """Create a task, execute its workflow, and persist the result."""

    user = session.exec(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True),
        )
    ).first()

    if not user:
        raise ValueError("Active user not found.")

    input_context = dict(task_data.input_context)

    order_number = extract_order_number(
        task_data.objective,
        input_context,
    )

    if not order_number:
        raise ValueError(
            "An order number (for example, ORD-1042) is required "
            "for the current workflow."
        )

    input_context["order_number"] = order_number

    task = OperationalTask(
        task_key=f"TASK-{uuid.uuid4().hex[:12].upper()}",
        user_id=user.id,
        objective=task_data.objective,
        priority=task_data.priority,
        input_context=input_context,
        status=TaskStatus.RUNNING,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    try:
        report = execute_task_workflow(task)

        task.final_report = report
        workflow_status = report.get("task_status")

        if workflow_status == "completed":
            task.status = TaskStatus.COMPLETED

        elif workflow_status == "waiting_for_approval":
            task.status = TaskStatus.WAITING_APPROVAL

        else:
            task.status = TaskStatus.FAILED

        if task.status in {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
        }:
            task.completed_at = utc_now()
        else:
            task.completed_at = None

    except Exception as exc:
        task.status = TaskStatus.FAILED
        task.final_report = {
            "task_id": str(task.id),
            "order_number": order_number,
            "task_status": "failed",
            "error": str(exc),
            "read_only": True,
            "execution_performed": False,
        }
        task.completed_at = utc_now()

    task.updated_at = utc_now()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task