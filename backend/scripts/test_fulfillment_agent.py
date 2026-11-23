
import json

from app.db.session import engine
from app.agents.fulfillment_agent import evaluate_fulfillment
from sqlmodel import Session


def main():
    with Session(engine) as session:
        result = evaluate_fulfillment(
            session,
            "ORD-1042",
        )

        print("\nFULFILLMENT AGENT RESULT\n")
        print(json.dumps(result, indent=4, default=str))

        assert result["success"] is True
        assert result["order_number"] == "ORD-1042"
        assert result["read_only"] is True
        assert result["execution_performed"] is False

        print("\nFULFILLMENT AGENT TEST PASSED")


if __name__ == "__main__":
    main()
