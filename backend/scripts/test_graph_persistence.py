
import json
import uuid

from sqlalchemy.engine import make_url
from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.agents.graph import build_graph


def main():
    # Convert SQLAlchemy's URL to a standard PostgreSQL URL
    database_url = make_url(settings.database_url)
    checkpoint_url = database_url.set(
        drivername="postgresql"
    ).render_as_string(hide_password=False)

    # Give this workflow execution its own persistent thread.
    thread_id = f"ORD-1042-{uuid.uuid4()}"

    initial_state = {
        "objective": (
            "Investigate delayed order ORD-1042, "
            "evaluate inventory, and recommend fulfillment."
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

    with PostgresSaver.from_conn_string(
        checkpoint_url
    ) as checkpointer:

        # Create checkpoint tables if they do not exist.
        checkpointer.setup()

        # Compile graph with PostgreSQL persistence.
        graph = build_graph(checkpointer=checkpointer)

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        result = graph.invoke(
            initial_state,
            config=config,
        )

        print("\nPERSISTENT WORKFLOW RESULT\n")
        print(json.dumps(
            result.get("final_report"),
            indent=4,
            default=str,
        ))

        # Confirm a checkpoint was saved.
        snapshot = graph.get_state(config)

        print("\nCHECKPOINT DETAILS")
        print("Thread ID:", thread_id)
        print("Checkpoint exists:", bool(snapshot.values))
        print("Task status:", snapshot.values.get("task_status"))

        assert result["final_report"]["task_status"] == "completed"
        assert result["final_report"]["verification"]["verified"] is True
        assert snapshot.values.get("final_report") is not None

        print("\nPOSTGRESQL CHECKPOINT TEST PASSED")


if __name__ == "__main__":
    main()
