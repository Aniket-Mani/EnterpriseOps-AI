
import json

from app.agents.orchestrator import create_execution_plan


if __name__ == "__main__":
    objective = (
        "Investigate delayed order ORD-1042. "
        "Determine whether inventory shortages or "
        "supplier delays are responsible and recommend "
        "the actions required to resolve the delay."
    )

    print("Submitting objective to Orchestrator...\n")

    try:
        plan = create_execution_plan(objective)

        print("ORCHESTRATOR PLAN GENERATED\n")
        print(json.dumps(plan, indent=4))

    except Exception as exc:
        print("ORCHESTRATOR FAILED")
        print(type(exc).__name__, str(exc))
