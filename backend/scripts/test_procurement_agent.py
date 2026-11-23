
import json

from sqlmodel import Session

from app.db.session import engine
from app.agents.procurement_agent import investigate_procurement


def test_procurement_investigation():
    required_items = [
        {"sku": "SKU-1001", "quantity": 5},
        {"sku": "SKU-1002", "quantity": 3},
    ]

    with Session(engine) as session:
        result = investigate_procurement(
            session,
            required_items,
        )

    assert result["success"] is True
    assert result["read_only"] is True
    assert result["products_investigated"] == 2

    print("\nPROCUREMENT AGENT RESULT\n")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    test_procurement_investigation()
