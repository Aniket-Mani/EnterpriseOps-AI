
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.db.models import Order, Inventory, Warehouse


def verify_fulfillment(
    session: Session,
    fulfillment_result: dict,
) -> dict:
    """
    Independently verifies fulfillment recommendations and
    warehouse allocations against current database records.

    Read-only: performs no operational changes.
    """

    if not fulfillment_result:
        raise ValueError("Fulfillment result is required.")

    order_number = fulfillment_result.get("order_number")

    if not order_number:
        raise ValueError("Fulfillment result has no order number.")

    if not fulfillment_result.get("success"):
        return {
            "agent": "verification",
            "success": True,
            "verified": False,
            "issues": ["The fulfillment evaluation was unsuccessful."],
            "read_only": True,
            "execution_performed": False,
        }

    # 1. Independently retrieve the order.
    statement = (
        select(Order)
        .where(Order.order_number == order_number)
        .options(selectinload(Order.items))
    )
    order = session.exec(statement).first()

    if order is None:
        return {
            "agent": "verification",
            "success": True,
            "verified": False,
            "issues": [f"Order {order_number} does not exist."],
            "read_only": True,
            "execution_performed": False,
        }

    issues = []
    checks = []

    # 2. Verify order quantities.
    expected_items = {
        item.product_sku: item.quantity
        for item in order.items
    }

    fulfillment_items = fulfillment_result.get("items", [])

    reported_items = {
        item.get("sku"): item.get("required_quantity")
        for item in fulfillment_items
    }

    if expected_items != reported_items:
        issues.append("Fulfillment quantities do not match the order.")
    else:
        checks.append("Order items and required quantities match.")

    # 3. Independently retrieve active warehouse inventory.
    inventory_statement = (
        select(Inventory)
        .join(
            Warehouse,
            Inventory.warehouse_id == Warehouse.id,
        )
        .where(Warehouse.is_active.is_(True))
    )

    inventory_records = session.exec(inventory_statement).all()

    inventory_by_sku = {}
    warehouse_inventory = {}

    for record in inventory_records:
        available = (
            record.quantity_on_hand - record.quantity_reserved
        )

        if (
            record.quantity_on_hand < 0
            or record.quantity_reserved < 0
            or record.quantity_reserved > record.quantity_on_hand
        ):
            issues.append(
                f"Invalid inventory quantities for {record.product_sku}."
            )
            continue

        warehouse = session.get(Warehouse, record.warehouse_id)

        if warehouse is None or not warehouse.is_active:
            continue

        inventory_by_sku[record.product_sku] = (
            inventory_by_sku.get(record.product_sku, 0)
            + available
        )

        warehouse_inventory[
            (record.product_sku, warehouse.warehouse_code)
        ] = {
            "available_quantity": available,
            "reorder_level": record.reorder_level,
        }

    # 4. Verify aggregate quantities and warehouse allocations.
    for item in fulfillment_items:
        sku = item.get("sku")
        required = item.get("required_quantity")
        reported_available = item.get("available_inventory")
        reported_allocated = item.get("allocated_quantity")
        reported_shortfall = item.get("inventory_shortfall")
        actual_available = inventory_by_sku.get(sku, 0)

        if not isinstance(required, int) or isinstance(required, bool) or required <= 0:
            issues.append(f"Invalid required quantity for {sku}.")
            continue

        if reported_available != actual_available:
            issues.append(
                f"Reported inventory for {sku} does not match database."
            )

        allocations = item.get("warehouse_allocations", [])

        allocated_total = 0
        seen_warehouses = set()

        for allocation in allocations:
            warehouse_code = allocation.get("warehouse_code")
            quantity = allocation.get("allocated_quantity")

            if (
                not isinstance(quantity, int)
                or isinstance(quantity, bool)
                or quantity <= 0
            ):
                issues.append(
                    f"Invalid allocation quantity for {sku} at {warehouse_code}."
                )
                continue

            if warehouse_code in seen_warehouses:
                issues.append(
                    f"Duplicate warehouse allocation for {sku} at {warehouse_code}."
                )
                continue

            seen_warehouses.add(warehouse_code)

            actual_warehouse = warehouse_inventory.get(
                (sku, warehouse_code)
            )

            if actual_warehouse is None:
                issues.append(
                    f"Allocation references inactive or unknown warehouse "
                    f"{warehouse_code} for {sku}."
                )
                continue

            warehouse_available = actual_warehouse["available_quantity"]
            reorder_level = actual_warehouse["reorder_level"]

            if quantity > warehouse_available:
                issues.append(
                    f"Allocation exceeds available stock for {sku} "
                    f"at {warehouse_code}."
                )
                continue

            expected_remaining = warehouse_available - quantity

            if allocation.get("remaining_available") != expected_remaining:
                issues.append(
                    f"Incorrect remaining inventory for {sku} at {warehouse_code}."
                )

            expected_below_reorder = expected_remaining < reorder_level

            if (
                allocation.get("below_reorder_level_after_allocation")
                != expected_below_reorder
            ):
                issues.append(
                    f"Incorrect reorder-level assessment for {sku} "
                    f"at {warehouse_code}."
                )

            allocated_total += quantity

        if reported_allocated != allocated_total:
            issues.append(
                f"Allocated quantity does not match warehouse allocations for {sku}."
            )

        actual_shortfall = max(0, required - allocated_total)

        if reported_shortfall != actual_shortfall:
            issues.append(
                f"Reported shortfall is incorrect for {sku}."
            )

        if allocated_total > required:
            issues.append(
                f"Allocated quantity exceeds the requirement for {sku}."
            )

        action = item.get("recommended_action")

        if actual_shortfall == 0:
            if action != "fulfill_from_allocated_inventory":
                issues.append(
                    f"Incorrect fulfillment action for {sku}."
                )
        elif action not in (
            "procure_shortfall",
            "requires_manual_review",
        ):
            issues.append(
                f"Invalid fulfillment action for {sku}."
            )

    if not any(
        "inventory" in issue.lower()
        or "allocation" in issue.lower()
        or "warehouse" in issue.lower()
        or "reorder" in issue.lower()
        or "shortfall" in issue.lower()
        for issue in issues
    ):
        checks.append(
            "Warehouse allocations match available stock and reorder levels."
        )

    # 5. Verify overall fulfillment status.
    actual_all_sufficient = all(
        item.get("required_quantity", 0)
        == item.get("allocated_quantity", 0)
        for item in fulfillment_items
    )

    all_items_have_path = all(
        item.get("recommended_action") != "requires_manual_review"
        for item in fulfillment_items
    )

    if actual_all_sufficient:
        expected_status = "inventory_fulfillment_possible"
    elif all_items_have_path:
        expected_status = "procurement_required"
    else:
        expected_status = "manual_review_required"

    if fulfillment_result.get("overall_status") != expected_status:
        issues.append("Overall fulfillment status is inconsistent.")

    # 6. Confirm that no operational execution was performed.
    if fulfillment_result.get("execution_performed") is not False:
        issues.append("Fulfillment result does not confirm read-only execution.")

    if fulfillment_result.get("read_only") is not True:
        issues.append("Fulfillment result does not confirm read-only operation.")

    verified = len(issues) == 0

    if verified:
        checks.append("Fulfillment actions and overall status are consistent.")

    return {
        "agent": "verification",
        "success": True,
        "verified": verified,
        "order_number": order_number,
        "checks_passed": checks,
        "issues": issues,
        "overall_status": (
            "verification_passed"
            if verified
            else "verification_failed"
        ),
        "read_only": True,
        "execution_performed": False,
    }
