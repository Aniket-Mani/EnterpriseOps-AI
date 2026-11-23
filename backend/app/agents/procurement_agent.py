from collections import defaultdict

from sqlmodel import Session, select

from app.db.models import (
    Supplier, SupplierProduct, PurchaseOrder, PurchaseOrderItem
)

def investigate_procurement(session: Session, required_items: list[dict],) -> dict:
    """
    Read-only procurement investigation.

    Compares active suppliers, prices, availability,
    minimum order quantities, lead times, and existing
    purchase orders.

    Does not create purchase orders or modify inventory.
    """

    if not required_items:
        raise ValueError("Required items cannot be empty.")

    # 1. Validate and combine duplicate SKUs.
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

    requested_skus = list(requirements.keys())

    # 2. Retrieve all active supplier offerings in one query.
    supplier_statement = (
        select(SupplierProduct, Supplier)
        .join(
            Supplier,
            SupplierProduct.supplier_id == Supplier.id,
        )
        .where(
            SupplierProduct.product_sku.in_(requested_skus),
            Supplier.is_active.is_(True),
        )
        .order_by(
            SupplierProduct.product_sku,
            SupplierProduct.unit_price,
        )
    )

    supplier_records = session.exec(supplier_statement).all()

    suppliers_by_sku = defaultdict(list)

    for product, supplier in supplier_records:
        suppliers_by_sku[product.product_sku].append(
            (product, supplier)
        )

    # 3. Retrieve existing purchase orders for requested SKUs.
    po_statement = (
        select(PurchaseOrderItem, PurchaseOrder, Supplier)
        .join(
            PurchaseOrder,
            PurchaseOrderItem.purchase_order_id == PurchaseOrder.id,
        )
        .join(
            Supplier,
            PurchaseOrder.supplier_id == Supplier.id,
        )
        .where(
            PurchaseOrderItem.product_sku.in_(requested_skus),
            PurchaseOrder.status != "cancelled",
        )
        .order_by(PurchaseOrder.expected_delivery)
    )

    po_records = session.exec(po_statement).all()

    purchase_orders_by_sku = defaultdict(list)

    for item, purchase_order, supplier in po_records:
        purchase_orders_by_sku[item.product_sku].append({
            "po_number": purchase_order.po_number,
            "supplier_code": supplier.supplier_code,
            "supplier_name": supplier.name,
            "status": purchase_order.status.value,
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
            "expected_delivery": (
                purchase_order.expected_delivery.isoformat()
                if purchase_order.expected_delivery
                else None
            ),
        })

    # 4. Investigate each requested product.
    products = []

    for sku, required_quantity in requirements.items():
        records = suppliers_by_sku.get(sku, [])

        supplier_options = []

        for product, supplier in records:
            meets_moq = (
                required_quantity >= product.minimum_order_quantity
            )

            suggested_order_quantity = max(
                required_quantity,
                product.minimum_order_quantity,
            )

            supplier_options.append({
                "supplier_code": supplier.supplier_code,
                "supplier_name": supplier.name,
                "unit_price": str(product.unit_price),
                "lead_time_days": product.lead_time_days,
                "minimum_order_quantity": (
                    product.minimum_order_quantity
                ),
                "is_available": product.is_available,
                "meets_moq": meets_moq,
                "suggested_order_quantity": (
                    suggested_order_quantity
                    if product.is_available
                    else None
                ),
                "estimated_total_cost": (
                    str(
                        product.unit_price
                        * suggested_order_quantity
                    )
                    if product.is_available
                    else None
                ),
                "eligible": product.is_available,
            })

        # Sort available options by price, then lead time.
        supplier_options.sort(
            key=lambda option: (
                not option["eligible"],
                float(option["unit_price"]),
                option["lead_time_days"],
            )
        )

        available_options = [
            option for option in supplier_options
            if option["eligible"]
        ]

        products.append({
            "sku": sku,
            "required_quantity": required_quantity,
            "supplier_found": len(records) > 0,
            "available_supplier_count": len(available_options),
            "supplier_options": supplier_options,
            "existing_purchase_orders": (
                purchase_orders_by_sku.get(sku, [])
            ),
            "investigation_status": (
                "options_found"
                if available_options
                else "no_available_supplier"
            ),
        })

    # 5. Return investigation report.
    return {
        "agent": "procurement",
        "success": True,
        "products_investigated": len(products),
        "products": products,
        "read_only": True,
    }
