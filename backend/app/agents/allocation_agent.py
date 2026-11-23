
def plan_warehouse_allocation(
    required_items: list[dict],
    inventory_result: dict,
) -> dict:
    """
    Build a deterministic, read-only warehouse allocation plan.

    Allocation priority:
    1. Preserve reorder levels wherever possible.
    2. Use stock from warehouses already below reorder level.
    3. Minimize new reorder-level violations.

    This function does not reserve, transfer, or modify inventory.
    """

    if not required_items:
        raise ValueError("Required items cannot be empty.")

    if not inventory_result.get("success"):
        raise ValueError("A successful inventory investigation is required.")

    inventory_by_sku = {
        product["sku"]: product
        for product in inventory_result.get("products", [])
    }

    allocations = []
    overall_sufficient = True
    warnings = []

    # Combine duplicate SKU requirements.
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

    for sku, required_quantity in requirements.items():
        product = inventory_by_sku.get(sku)

        if not product or not product.get("inventory_found"):
            allocations.append({
                "sku": sku,
                "required_quantity": required_quantity,
                "allocated_quantity": 0,
                "shortfall": required_quantity,
                "warehouse_allocations": [],
                "sufficient": False,
            })
            overall_sufficient = False
            continue

        # Work on copies. Never mutate the inventory investigation.
        warehouses = []

        for warehouse in product.get("warehouses", []):
            available = warehouse["available_quantity"]
            reorder_level = warehouse["reorder_level"]

            if (
                not isinstance(available, int)
                or isinstance(available, bool)
                or not isinstance(reorder_level, int)
                or isinstance(reorder_level, bool)
                or available < 0
                or reorder_level < 0
            ):
                raise ValueError(
                    f"Invalid inventory data for SKU {sku}."
                )

            warehouses.append({
                "warehouse_code": warehouse["warehouse_code"],
                "warehouse_name": warehouse["warehouse_name"],
                "available_quantity": available,
                "reorder_level": reorder_level,
                "remaining_quantity": available,
            })

        # Phase 1: use stock above reorder levels.
        safe_priority = sorted(
            warehouses,
            key=lambda warehouse: (
                -max(
                    0,
                    warehouse["available_quantity"]
                    - warehouse["reorder_level"],
                ),
                warehouse["warehouse_code"],
            ),
        )

        remaining_required = required_quantity
        warehouse_allocations = []

        def allocate_from(warehouse, quantity):
            """Allocate stock and consolidate warehouse entries."""
            existing = next(
                (
                    allocation
                    for allocation in warehouse_allocations
                    if allocation["warehouse_code"]
                    == warehouse["warehouse_code"]
                ),
                None,
            )

            if existing:
                existing["allocated_quantity"] += quantity
            else:
                warehouse_allocations.append({
                    "warehouse_code": warehouse["warehouse_code"],
                    "warehouse_name": warehouse["warehouse_name"],
                    "allocated_quantity": quantity,
                })

            warehouse["remaining_quantity"] -= quantity

        for warehouse in safe_priority:
            if remaining_required <= 0:
                break

            safe_quantity = max(
                0,
                warehouse["remaining_quantity"]
                - warehouse["reorder_level"],
            )

            quantity_to_allocate = min(
                safe_quantity,
                remaining_required,
            )

            if quantity_to_allocate > 0:
                allocate_from(warehouse, quantity_to_allocate)
                remaining_required -= quantity_to_allocate

        # Phase 2: use stock from warehouses already below
        # their reorder level before creating new violations.
        already_below_priority = sorted(
            [
                warehouse
                for warehouse in warehouses
                if warehouse["remaining_quantity"] > 0
                and warehouse["remaining_quantity"]
                < warehouse["reorder_level"]
            ],
            key=lambda warehouse: (
                warehouse["remaining_quantity"],
                warehouse["warehouse_code"],
            ),
        )

        for warehouse in already_below_priority:
            if remaining_required <= 0:
                break

            quantity_to_allocate = min(
                warehouse["remaining_quantity"],
                remaining_required,
            )

            if quantity_to_allocate > 0:
                allocate_from(warehouse, quantity_to_allocate)
                remaining_required -= quantity_to_allocate

        # Phase 3: if still necessary, consume stock that would
        # newly push a warehouse below its reorder level.
        remaining_priority = sorted(
            [
                warehouse
                for warehouse in warehouses
                if warehouse["remaining_quantity"] > 0
            ],
            key=lambda warehouse: (
                -warehouse["remaining_quantity"],
                warehouse["warehouse_code"],
            ),
        )

        for warehouse in remaining_priority:
            if remaining_required <= 0:
                break

            quantity_to_allocate = min(
                warehouse["remaining_quantity"],
                remaining_required,
            )

            if quantity_to_allocate > 0:
                allocate_from(warehouse, quantity_to_allocate)
                remaining_required -= quantity_to_allocate

        # Calculate final remaining stock and reorder impact.
        for allocation in warehouse_allocations:
            warehouse = next(
                item for item in warehouses
                if item["warehouse_code"] == allocation["warehouse_code"]
            )

            remaining_available = warehouse["remaining_quantity"]
            reorder_level = warehouse["reorder_level"]

            below_reorder = remaining_available < reorder_level

            allocation["remaining_available"] = remaining_available
            allocation["reorder_level"] = reorder_level
            allocation["below_reorder_level_after_allocation"] = below_reorder

            if below_reorder:
                warnings.append(
                    f"{sku} allocation leaves "
                    f"{warehouse['warehouse_code']} below its "
                    "reorder level."
                )

        allocated_quantity = required_quantity - remaining_required
        sufficient = remaining_required == 0

        if not sufficient:
            overall_sufficient = False

        allocations.append({
            "sku": sku,
            "product_name": product.get("product_name"),
            "required_quantity": required_quantity,
            "allocated_quantity": allocated_quantity,
            "shortfall": remaining_required,
            "warehouse_allocations": warehouse_allocations,
            "sufficient": sufficient,
        })

    return {
        "agent": "allocation",
        "success": True,
        "overall_sufficient": overall_sufficient,
        "items": allocations,
        "warnings": warnings,
        "read_only": True,
        "execution_performed": False,
    }
