
from collections import defaultdict

from sqlmodel import Session, select

from app.db.models import Inventory, Warehouse


def investigate_inventory(
    session: Session,
    required_items: list[dict],
) -> dict:
    """
    Read-only inventory investigation.

    Checks whether requested quantities are available across
    all active warehouses. Does not reserve, transfer, or
    modify inventory.
    """

    if not required_items:
        raise ValueError("Required items cannot be empty.")

    # 1. Validate input and combine duplicate SKUs.
    requirements = {}

    for item in required_items:
        sku = item.get("sku")
        quantity = item.get("quantity")

        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("Every item must have a valid SKU.")

        if (
            not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            raise ValueError(f"Invalid quantity for SKU {sku}.")

        sku = sku.strip()
        requirements[sku] = requirements.get(sku, 0) + quantity

    # 2. Fetch all requested SKUs in ONE database query.
    statement = (
        select(Inventory, Warehouse)
        .join(
            Warehouse,
            Inventory.warehouse_id == Warehouse.id,
        )
        .where(
            Inventory.product_sku.in_(list(requirements.keys())),
            Warehouse.is_active.is_(True),
        )
        .order_by(
            Inventory.product_sku,
            Warehouse.warehouse_code,
        )
    )

    records = session.exec(statement).all()

    # 3. Group inventory records by SKU.
    inventory_by_sku = defaultdict(list)

    for inventory, warehouse in records:
        inventory_by_sku[inventory.product_sku].append(
            (inventory, warehouse)
        )

    # 4. Investigate each requested SKU.
    products = []
    overall_sufficient = True

    for sku, required_quantity in requirements.items():
        sku_records = inventory_by_sku.get(sku, [])

        if not sku_records:
            overall_sufficient = False

            products.append({
                "sku": sku,
                "required_quantity": required_quantity,
                "inventory_found": False,
                "total_available": 0,
                "shortfall": required_quantity,
                "sufficient": False,
                "warehouses": [],
            })

            continue

        warehouse_results = []
        total_available = 0

        for inventory, warehouse in sku_records:
            available = inventory.available_quantity

            # Detect invalid inventory data instead of
            # reporting misleading availability.
            if (
                inventory.quantity_on_hand < 0
                or inventory.quantity_reserved < 0
                or inventory.quantity_reserved > inventory.quantity_on_hand
            ):
                raise ValueError(
                    f"Invalid inventory quantities for SKU {sku} "
                    f"in warehouse {warehouse.warehouse_code}."
                )

            total_available += available

            warehouse_results.append({
                "warehouse_code": warehouse.warehouse_code,
                "warehouse_name": warehouse.name,
                "quantity_on_hand": inventory.quantity_on_hand,
                "quantity_reserved": inventory.quantity_reserved,
                "available_quantity": available,
                "reorder_level": inventory.reorder_level,
                "below_reorder_level": (
                    available < inventory.reorder_level
                ),
            })

        shortfall = max(0, required_quantity - total_available)
        sufficient = shortfall == 0

        if not sufficient:
            overall_sufficient = False

        products.append({
            "sku": sku,
            "product_name": sku_records[0][0].product_name,
            "required_quantity": required_quantity,
            "inventory_found": True,
            "total_available": total_available,
            "shortfall": shortfall,
            "sufficient": sufficient,
            "warehouses": warehouse_results,
        })

    # 5. Return read-only investigation report.
    return {
        "agent": "inventory",
        "success": True,
        "overall_sufficient": overall_sufficient,
        "products_investigated": len(products),
        "products": products,
    }
