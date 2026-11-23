import uuid

from sqlmodel import Session

from app.db.models import ApprovalRequest, ApprovalStatus
from app.db.session import engine


TASK_ID = uuid.UUID(
    "c04bcdec-9cd8-4f40-800b-acd12f301690"
)


def main():
    with Session(engine) as session:
        approval = ApprovalRequest(
            task_id=TASK_ID,
            agent_run_id=None,
            action_type="test_only_no_execution",
            description=(
                "Development test: simulate approval of a proposed "
                "inventory fulfillment recommendation for ORD-1042. "
                "This request must not trigger any operational action."
            ),
            requested_action={
                "order_number": "ORD-1042",
                "action": "simulated_inventory_fulfillment",
                "simulation": True,
                "execution_enabled": False,
            },
            status=ApprovalStatus.PENDING,
        )

        session.add(approval)
        session.commit()
        session.refresh(approval)

        print("Test approval request created.")
        print(f"Approval ID: {approval.id}")
        print(f"Task ID: {approval.task_id}")
        print(f"Status: {approval.status.value}")
        print("Execution enabled: False")


if __name__ == "__main__":
    main()