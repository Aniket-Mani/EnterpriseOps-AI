
import json

from sqlmodel import Session

from app.db.session import engine
from app.agents.fulfillment_agent import evaluate_fulfillment
from app.agents.verification_agent import verify_fulfillment


def main():
    with Session(engine) as session:

        # First generate a fulfillment recommendation.
        fulfillment_result = evaluate_fulfillment(
            session,
            "ORD-1042",
        )

        # Independently verify that recommendation.
        verification_result = verify_fulfillment(
            session,
            fulfillment_result,
        )

        print("\nVERIFICATION AGENT RESULT\n")
        print(json.dumps(
            verification_result,
            indent=4,
            default=str,
        ))

        assert verification_result["success"] is True
        assert verification_result["verified"] is True
        assert verification_result["read_only"] is True

        print("\nVERIFICATION AGENT TEST PASSED")


if __name__ == "__main__":
    main()
