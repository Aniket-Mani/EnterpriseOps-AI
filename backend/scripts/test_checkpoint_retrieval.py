
from sqlalchemy.engine import make_url
from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.agents.graph import build_graph


THREAD_ID = "ORD-1042-75668123-8385-4134-b748-fe5dbe123e4e"


def main():
    database_url = make_url(settings.database_url)

    checkpoint_url = database_url.set(
        drivername="postgresql"
    ).render_as_string(hide_password=False)

    with PostgresSaver.from_conn_string(
        checkpoint_url
    ) as checkpointer:

        graph = build_graph(checkpointer=checkpointer)

        config = {
            "configurable": {
                "thread_id": THREAD_ID,
            }
        }

        snapshot = graph.get_state(config)

        print("\nRETRIEVED WORKFLOW STATE\n")
        print("Thread ID:", THREAD_ID)
        print("Checkpoint found:", bool(snapshot.values))
        print("Task status:", snapshot.values.get("task_status"))

        report = snapshot.values.get("final_report", {})

        print("Order:", report.get("order_number"))
        print("Verification:", report.get("verification", {}).get("verified"))

        assert snapshot.values
        assert report
        assert report["order_number"] == "ORD-1042"
        assert report["verification"]["verified"] is True

        print("\nCHECKPOINT RETRIEVAL TEST PASSED")


if __name__ == "__main__":
    main()
