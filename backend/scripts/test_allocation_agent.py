
from sqlmodel import Session

from app.db.session import engine
from app.agents.inventory_agent import investigate_inventory
from app.agents.allocation_agent import plan_warehouse_allocation


def main():
    required_items = [
        {"sku": "SKU-1001", "quantity": 5},
        {"sku": "SKU-1002", "quantity": 3},
    ]

    with Session(engine) as session:
        inventory_result = investigate_inventory(
            session,
            required_items,
        )

    allocation_result = plan_warehouse_allocation(
        required_items,
        inventory_result,
    )

    print("\nWAREHOUSE ALLOCATION PLAN\n")
    print(allocation_result)

    assert allocation_result["success"] is True
    assert allocation_result["overall_sufficient"] is True
    assert allocation_result["read_only"] is True
    assert allocation_result["execution_performed"] is False

    allocations = {
        item["sku"]: item
        for item in allocation_result["items"]
    }

    assert allocations["SKU-1001"]["allocated_quantity"] == 5
    assert allocations["SKU-1002"]["allocated_quantity"] == 3

    for item in allocation_result["items"]:
        assert (
            item["allocated_quantity"] + item["shortfall"]
            == item["required_quantity"]
        )

    print("\nALLOCATION AGENT TEST PASSED")


if __name__ == "__main__":
    main()
