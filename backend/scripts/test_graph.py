
import json

from app.agents.graph import enterpriseops_graph


def main():
    initial_state = {
        "objective": (
            "Investigate delayed order ORD-1042, "
            "evaluate available inventory, and recommend "
            "a fulfillment strategy."
        ),
        "order_number": "ORD-1042",
        "task_context": {
            "order_number": "ORD-1042",
        },
        "task_status": "running",
        "messages": [],
        "agent_results": [],
        "errors": [],
        "audit_events": [],
    }

    result = enterpriseops_graph.invoke(initial_state)

    print("\nENTERPRISEOPS AI WORKFLOW RESULT\n")
    print(json.dumps(
        result.get("final_report"),
        indent=4,
        default=str,
    ))

    print("\nAGENT EXECUTION SUMMARY\n")

    for agent_result in result.get("agent_results", []):
        print(
            f"{agent_result.get('agent')}: "
            f"{'SUCCESS' if agent_result.get('success') else 'FAILED'}"
        )

    assert result.get("final_report") is not None
    assert result["final_report"]["task_status"] == "completed"
    assert result["final_report"]["verification"]["verified"] is True
    assert result["final_report"]["read_only"] is True
    assert result["final_report"]["execution_performed"] is False

    print("\nENTERPRISEOPS AI WORKFLOW TEST PASSED")


if __name__ == "__main__":
    main()
