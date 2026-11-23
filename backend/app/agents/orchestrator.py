
import json

from app.agents.model_router import generate_response
from app.schemas.execution_plan import ExecutionPlan


ORCHESTRATOR_SYSTEM_PROMPT = """
You are the Orchestrator of EnterpriseOps AI, an autonomous
enterprise operations platform.

Understand the objective, identify the problem, and create
a structured plan using specialist agents.

Available specialist agents:
- order: Investigates customer orders and order status.
- inventory: Checks stock levels across warehouses.
- procurement: Investigates suppliers and purchasing options.
- fulfillment: Coordinates fulfillment planning.
- verification: Independently verifies results.

Rules:
- Use only the available specialist agents.
- Include every required agent in both agents_required
  and execution_plan.
- Include verification whenever verification_required is true.
- Number steps sequentially starting at 1.
- Dependencies must refer only to earlier steps.
- Use depends_on: [] when a step has no dependencies.
- Never claim an action has been executed.
- Do not invent operational data.
- Identify actions that require human approval.
- Return valid JSON without Markdown.

Return this exact structure:
{
    "task_type": "routine or complex",
    "problem_summary": "Short description of the problem",
    "priority": "low, medium, high or critical",
    "agents_required": ["order", "inventory", "verification"],
    "execution_plan": [
        {
            "step": 1,
            "agent": "order",
            "action": "Investigate the order",
            "expected_output": "Order status and details",
            "depends_on": []
        },
        {
            "step": 2,
            "agent": "inventory",
            "action": "Investigate stock",
            "expected_output": "Warehouse availability",
            "depends_on": [1]
        },
        {
            "step": 3,
            "agent": "verification",
            "action": "Verify investigation results",
            "expected_output": "Independent verification",
            "depends_on": [1, 2]
        }
    ],
    "requires_human_approval": false,
    "verification_required": true
}
"""


def create_execution_plan(
    objective: str,
    context: dict | None = None,
) -> dict:
    if not objective or not objective.strip():
        raise ValueError("Objective cannot be empty.")

    context = context or {}

    prompt = f"""{ORCHESTRATOR_SYSTEM_PROMPT}

USER OBJECTIVE:
{objective}

ADDITIONAL CONTEXT:
{json.dumps(context, default=str)}

Determine whether this is a routine or complex task.
Return only the requested JSON object.
"""

    result = generate_response(
        prompt=prompt,
        task_type="complex",
    )

    try:
        raw_plan = json.loads(result["text"])
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(
            "Orchestrator returned invalid JSON."
        ) from exc

    try:
        validated_plan = ExecutionPlan.model_validate(raw_plan)
    except Exception as exc:
        raise ValueError(
            f"Orchestrator returned an invalid execution plan: {exc}"
        ) from exc

    plan = validated_plan.model_dump(mode="json")
    plan["model_used"] = result["model"]

    return plan
