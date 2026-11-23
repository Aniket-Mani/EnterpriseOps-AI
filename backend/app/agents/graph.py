
from datetime import datetime, timezone
from uuid import UUID

from langgraph.graph import StateGraph, START, END
from sqlmodel import Session
from sqlalchemy import select as sa_select

from app.db.session import engine
from app.agents.state import EnterpriseOpsState
from app.agents.orchestrator import create_execution_plan
from app.agents.order_agent import investigate_order
from app.agents.inventory_agent import investigate_inventory
from app.agents.procurement_agent import investigate_procurement
from app.agents.fulfillment_agent import evaluate_fulfillment
from app.agents.verification_agent import verify_fulfillment
from app.db.models import ApprovalRequest, ApprovalStatus
from app.services.agent_persistence import persist_agent_execution


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def get_order_number(state: EnterpriseOpsState) -> str:
    order_number = (
        state.get("order_number")
        or state.get("task_context", {}).get("order_number")
    )

    if not order_number:
        raise ValueError("An order number is required.")

    return order_number.strip()


def get_task_id(state: EnterpriseOpsState):
    raw_task_id = state.get("task_id")

    if not raw_task_id:
        return None

    return UUID(str(raw_task_id))


def orchestrator_node(state: EnterpriseOpsState) -> dict:
    try:
        objective = state.get("objective") or (
            f"Investigate and evaluate fulfillment for order "
            f"{get_order_number(state)}."
        )

        started_at = datetime.now(timezone.utc)

        plan = create_execution_plan(
            objective=objective,
            context=state.get("task_context", {}),
        )

        task_id = get_task_id(state)

        if task_id:
            with Session(engine) as session:
                persist_agent_execution(
                    session,
                    task_id=task_id,
                    agent="orchestrator",
                    input_data={
                        "objective": objective,
                        "task_context": state.get("task_context", {}),
                    },
                    output_data=plan,
                    started_at=started_at,
                )
                session.commit()

        return {
            "execution_plan": plan,
            "completed_steps": [],
            "step_results": {},
            "task_status": "running",
            "messages": [{
                "sender": "orchestrator",
                "content": "Validated execution plan created.",
                "timestamp": timestamp(),
            }],
            "agent_results": [{
                "agent": "orchestrator",
                "success": True,
                "result": plan,
            }],
            "audit_events": [{
                "event": "execution_plan_created",
                "timestamp": timestamp(),
                "agents_required": plan["agents_required"],
            }],
        }

    except Exception as exc:
        return {
            "errors": [f"Orchestrator error: {exc}"],
            "task_status": "failed",
        }


def run_agent(
    agent: str,
    state: EnterpriseOpsState,
    session: Session,
) -> dict:

    order_number = get_order_number(state)

    if agent == "order":
        return investigate_order(session, order_number)

    if agent == "inventory":
        order_result = state.get("order_result") or {}

        if not order_result.get("success"):
            raise ValueError(
                "Successful order investigation is required."
            )

        required_items = [
            {
                "sku": item["sku"],
                "quantity": item["quantity"],
            }
            for item in order_result.get("items", [])
        ]

        return investigate_inventory(session, required_items)

    if agent == "procurement":
        inventory = state.get("inventory_result") or {}

        if not inventory.get("success"):
            raise ValueError(
                "Successful inventory investigation is required."
            )

        requirements = [
            {
                "sku": product["sku"],
                "quantity": product["shortfall"],
            }
            for product in inventory.get("products", [])
            if product.get("shortfall", 0) > 0
        ]

        if not requirements:
            return {
                "agent": "procurement",
                "success": True,
                "not_required": True,
                "products": [],
                "read_only": True,
            }

        return investigate_procurement(session, requirements)

    if agent == "fulfillment":
        return evaluate_fulfillment(
            session,
            order_number,
            inventory_result=state.get("inventory_result"),
            procurement_result=state.get("procurement_result"),
        )

    if agent == "verification":
        fulfillment = state.get("fulfillment_result")

        if not fulfillment:
            raise ValueError("Fulfillment result is required.")

        return verify_fulfillment(session, fulfillment)

    raise ValueError(
        f"Unsupported agent in execution plan: {agent}"
    )


def execute_next_step_node(state: EnterpriseOpsState) -> dict:

    plan = state.get("execution_plan") or {}
    steps = plan.get("execution_plan", [])

    completed = list(state.get("completed_steps", []))
    step_results = dict(state.get("step_results", {}))

    if len(completed) == len(steps):
        return {}

    next_step = next(
        (
            step
            for step in steps
            if step["step"] not in completed
            and all(
                dependency in completed
                for dependency in step.get("depends_on", [])
            )
        ),
        None,
    )

    if next_step is None:
        error_message = (
            "Execution plan cannot progress: unresolved dependencies."
        )

        return {
            "errors": [error_message],
            "task_status": "failed",
            "audit_events": [{
                "event": "agent_step_failed",
                "error": error_message,
                "timestamp": timestamp(),
            }],
        }

    agent = next_step["agent"]
    task_id = get_task_id(state)
    started_at = datetime.now(timezone.utc)

    input_data = {
        "step": next_step,
        "objective": state.get("objective"),
        "order_number": state.get("order_number"),
        "task_context": state.get("task_context", {}),
        "dependency_results": {
            str(dependency): step_results.get(str(dependency))
            for dependency in next_step.get("depends_on", [])
        },
    }

    try:
        # Execute the agent and persist its successful result.
        with Session(engine) as session:
            result = run_agent(agent, state, session)

            if not result.get("success"):
                raise RuntimeError(
                    result.get(
                        "error",
                        f"{agent} agent reported failure.",
                    )
                )

            if task_id:
                persist_agent_execution(
                    session,
                    task_id=task_id,
                    agent=agent,
                    input_data=input_data,
                    output_data=result,
                    started_at=started_at,
                )

            session.commit()

        result_key = f"{agent}_result"

        step_results[str(next_step["step"])] = result
        completed.append(next_step["step"])

        return {
            result_key: result,
            "step_results": step_results,
            "completed_steps": completed,
            "current_agent": agent,
            "task_status": "running",
            "agent_results": [{
                "agent": agent,
                "success": True,
                "step": next_step["step"],
                "result": result,
            }],
            "messages": [{
                "sender": agent,
                "content": (
                    f"Execution step {next_step['step']} completed."
                ),
                "timestamp": timestamp(),
            }],
            "audit_events": [{
                "event": "agent_step_completed",
                "agent": agent,
                "step": next_step["step"],
                "timestamp": timestamp(),
            }],
        }

    except Exception as exc:
        error_message = str(exc)

        # Record failure independently so it survives rollback.
        if task_id:
            try:
                with Session(engine) as session:
                    persist_agent_execution(
                        session,
                        task_id=task_id,
                        agent=agent,
                        input_data=input_data,
                        output_data={},
                        error=error_message,
                        started_at=started_at,
                    )
                    session.commit()

            except Exception as persistence_error:
                error_message += (
                    f"; persistence error: {persistence_error}"
                )

        return {
            "errors": [
                f"Agent execution error: {error_message}"
            ],
            "task_status": "failed",
            "audit_events": [{
                "event": "agent_step_failed",
                "agent": agent,
                "step": next_step["step"],
                "error": error_message,
                "timestamp": timestamp(),
            }],
        }


def route_after_step(state: EnterpriseOpsState) -> str:

    if state.get("task_status") == "failed":
        return "report"

    plan = state.get("execution_plan") or {}
    steps = plan.get("execution_plan", [])
    completed = state.get("completed_steps", [])

    if len(completed) < len(steps):
        return "execute"

    if not state.get("verification_result", {}).get("verified"):
        return "report"

    if (
        state.get("task_id")
        and plan.get("requires_human_approval")
    ):
        return "approval"

    return "report"


def approval_node(state: EnterpriseOpsState) -> dict:
    try:
        plan = state.get("execution_plan") or {}
        verification = state.get("verification_result") or {}

        if not plan.get("requires_human_approval"):
            return {"requires_human_approval": False}

        if not verification.get("verified"):
            return {
                "task_status": "needs_review",
                "errors": [
                    "Approval was not created because verification failed."
                ],
            }

        task_id = get_task_id(state)

        if not task_id:
            raise ValueError(
                "Task ID is required for persistent approval."
            )

        order_number = get_order_number(state)
        fulfillment = state.get("fulfillment_result") or {}

        action_type = "review_fulfillment_recommendation"

        with Session(engine) as session:
            existing = session.exec(
                sa_select(ApprovalRequest).where(
                    ApprovalRequest.task_id == task_id,
                    ApprovalRequest.action_type == action_type,
                    ApprovalRequest.status != ApprovalStatus.CANCELLED,
                )
            ).scalars().first()

            if existing:
                approval = existing

            else:
                approval = ApprovalRequest(
                    task_id=task_id,
                    agent_run_id=None,
                    action_type=action_type,
                    description=(
                        f"Review the verified fulfillment recommendation "
                        f"for order {order_number}. This does not authorize "
                        "operational execution."
                    ),
                    requested_action={
                        "order_number": order_number,
                        "action": action_type,
                        "fulfillment_evaluation": fulfillment,
                        "verification": verification,
                        "simulation": True,
                        "execution_enabled": False,
                    },
                    status=ApprovalStatus.PENDING,
                )

                session.add(approval)
                session.commit()
                session.refresh(approval)

            approval_data = {
                "approval_id": str(approval.id),
                "task_id": str(task_id),
                "action_type": approval.action_type,
                "status": approval.status.value,
                "execution_enabled": False,
            }

        return {
            "pending_approvals": [approval_data],
            "requires_human_approval": True,
            "task_status": (
                "waiting_for_approval"
                if approval.status == ApprovalStatus.PENDING
                else "needs_review"
            ),
            "messages": [{
                "sender": "orchestrator",
                "content": "Approval request recorded.",
                "timestamp": timestamp(),
            }],
            "audit_events": [{
                "event": "approval_request_created",
                "approval_id": str(approval.id),
                "timestamp": timestamp(),
            }],
        }

    except Exception as exc:
        return {
            "errors": [f"Approval node error: {exc}"],
            "task_status": "needs_review",
        }


def report_node(state: EnterpriseOpsState) -> dict:

    errors = state.get("errors", [])
    verification = state.get("verification_result") or {}
    plan = state.get("execution_plan") or {}
    completed_steps = state.get("completed_steps", [])
    steps = plan.get("execution_plan", [])
    pending_approvals = state.get("pending_approvals", [])

    if errors:
        status = "failed"

    elif pending_approvals:
        status = "waiting_for_approval"

    elif (
        len(completed_steps) == len(steps)
        and verification.get("verified") is True
    ):
        status = "completed"

    else:
        status = "needs_review"

    report = {
        "objective": state.get("objective"),
        "order_number": state.get("order_number"),
        "task_status": status,
        "execution_plan": plan,
        "completed_steps": completed_steps,
        "step_results": state.get("step_results", {}),
        "order_investigation": state.get("order_result"),
        "inventory_investigation": state.get("inventory_result"),
        "procurement_investigation": state.get("procurement_result"),
        "fulfillment_evaluation": state.get("fulfillment_result"),
        "verification": verification,
        "errors": errors,
        "read_only": True,
        "execution_performed": False,
        "generated_at": timestamp(),
        "pending_approvals": pending_approvals,
        "requires_human_approval": bool(pending_approvals),
    }

    return {
        "final_report": report,
        "task_status": status,
        "messages": [{
            "sender": "orchestrator",
            "content": f"Workflow finished with status: {status}.",
            "timestamp": timestamp(),
        }],
        "audit_events": [{
            "event": "workflow_completed",
            "task_status": status,
            "timestamp": timestamp(),
        }],
    }


def build_graph(checkpointer=None):

    workflow = StateGraph(EnterpriseOpsState)

    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("execute_step", execute_next_step_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("report", report_node)

    workflow.add_edge(START, "orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        lambda state: (
            "execute_step"
            if state.get("task_status") != "failed"
            else "report"
        ),
        {
            "execute_step": "execute_step",
            "report": "report",
        },
    )

    workflow.add_conditional_edges(
        "execute_step",
        route_after_step,
        {
            "execute": "execute_step",
            "approval": "approval",
            "report": "report",
        },
    )

    workflow.add_edge("approval", "report")
    workflow.add_edge("report", END)

    return workflow.compile(checkpointer=checkpointer)


enterpriseops_graph = build_graph()
