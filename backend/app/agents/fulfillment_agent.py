
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.db.models import Order
from app.agents.inventory_agent import investigate_inventory
from app.agents.allocation_agent import plan_warehouse_allocation
from app.agents.procurement_agent import investigate_procurement


def evaluate_fulfillment(
    session: Session,
    order_number: str,
    inventory_result: dict | None = None,
    procurement_result: dict | None = None,
) -> dict:
    """
    Build a read-only fulfillment recommendation from independently
    gathered order, inventory, and procurement information.
    """

    if not order_number or not order_number.strip():
        raise ValueError("Order number is required.")

    statement = (
        select(Order)
        .where(Order.order_number == order_number.strip())
        .options(selectinload(Order.items))
    )
    order = session.exec(statement).first()

    if order is None:
        return {
            "agent": "fulfillment",
            "success": False,
            "error": f"Order {order_number} was not found.",
        }

    if not order.items:
        return {
            "agent": "fulfillment",
            "success": False,
            "error": f"Order {order_number} has no items.",
        }

    required_items = [
        {"sku": item.product_sku, "quantity": item.quantity}
        for item in order.items
    ]

    if inventory_result is None:
        inventory_result = investigate_inventory(session, required_items)

    if not inventory_result.get("success"):
        return {
            "agent": "fulfillment",
            "success": False,
            "error": "Inventory investigation failed.",
            "inventory_investigation": inventory_result,
        }

    allocation_result = plan_warehouse_allocation(
        required_items,
        inventory_result,
    )

    allocation_by_sku = {
        item["sku"]: item for item in allocation_result["items"]
    }
    inventory_by_sku = {
        product["sku"]: product
        for product in inventory_result["products"]
    }

    fulfillment_items = []
    procurement_requirements = []

    for item in required_items:
        sku = item["sku"]
        required = item["quantity"]

        inventory = inventory_by_sku.get(sku, {})
        allocation = allocation_by_sku.get(sku, {})

        allocated = allocation.get("allocated_quantity", 0)
        shortfall = max(0, required - allocated)

        fulfillment_items.append({
            "sku": sku,
            "required_quantity": required,
            "available_inventory": inventory.get("total_available", 0),
            "allocated_quantity": allocated,
            "inventory_shortfall": shortfall,
            "inventory_sufficient": shortfall == 0,
            "warehouse_allocations": allocation.get(
                "warehouse_allocations", []
            ),
            "allocation_warnings": [
                warning
                for warning in allocation_result.get("warnings", [])
                if sku in warning
            ],
        })

        if shortfall > 0:
            procurement_requirements.append({
                "sku": sku,
                "quantity": shortfall,
            })

    if procurement_requirements and procurement_result is None:
        procurement_result = investigate_procurement(
            session,
            procurement_requirements,
        )

    if procurement_result is not None and not procurement_result.get("success"):
        return {
            "agent": "fulfillment",
            "success": False,
            "error": "Procurement investigation failed.",
            "inventory_investigation": inventory_result,
            "allocation_plan": allocation_result,
            "procurement_investigation": procurement_result,
        }

    procurement_by_sku = {
        product["sku"]: product
        for product in (procurement_result or {}).get("products", [])
    }

    for item in fulfillment_items:
        if item["inventory_sufficient"]:
            item["recommended_action"] = "fulfill_from_allocated_inventory"
            item["supplier_options"] = []
            continue

        procurement = procurement_by_sku.get(item["sku"], {})
        eligible_options = [
            option
            for option in procurement.get("supplier_options", [])
            if option.get("eligible")
        ]

        item["supplier_options"] = eligible_options
        item["recommended_action"] = (
            "procure_shortfall"
            if eligible_options
            else "requires_manual_review"
        )

    all_inventory_sufficient = all(
        item["inventory_sufficient"] for item in fulfillment_items
    )
    all_items_have_path = all(
        item["recommended_action"] != "requires_manual_review"
        for item in fulfillment_items
    )

    if all_inventory_sufficient:
        overall_status = "inventory_fulfillment_possible"
    elif all_items_have_path:
        overall_status = "procurement_required"
    else:
        overall_status = "manual_review_required"

    return {
        "agent": "fulfillment",
        "success": True,
        "order_number": order.order_number,
        "order_status": order.status.value,
        "overall_status": overall_status,
        "items": fulfillment_items,
        "inventory_investigation": inventory_result,
        "allocation_plan": allocation_result,
        "procurement_investigation": procurement_result,
        "read_only": True,
        "execution_performed": False,
    }
