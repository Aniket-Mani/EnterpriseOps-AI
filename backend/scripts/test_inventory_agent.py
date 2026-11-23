
import json

from sqlmodel import Session

from app.db.session import engine
from app.agents.inventory_agent import investigate_inventory


def test_inventory_investigation():
    required_items = [
        {"sku": "SKU-1001", "quantity": 5},
        {"sku": "SKU-1002", "quantity": 3},
    ]

    with Session(engine) as session:
        result = investigate_inventory(session, required_items)

    assert result["success"] is True
    assert result["overall_sufficient"] is True
    assert result["products_investigated"] == 2

    print("\nINVENTORY AGENT RESULT\n")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    test_inventory_investigation()
