
import operator
import uuid

from typing import Annotated, TypedDict
from app.db.models.agent_run import AgentType


class EnterpriseOpsState(TypedDict, total=False):
    task_id: uuid.UUID
    objective: str
    task_context: dict
    order_number: str

    execution_plan: dict
    current_agent: AgentType | None

    order_result: dict
    inventory_result: dict
    procurement_result: dict
    fulfillment_result: dict
    verification_result: dict

    completed_steps: list[int]
    step_results: dict

    messages: Annotated[list[dict], operator.add]
    agent_results: Annotated[list[dict], operator.add]
    pending_approvals: Annotated[list[dict], operator.add]
    requires_human_approval: bool

    errors: Annotated[list[str], operator.add]
    audit_events: Annotated[list[dict], operator.add]

    final_report: dict | None
    task_status: str
    attempt_count: int
