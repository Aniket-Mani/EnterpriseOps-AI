from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.db.models import Order

class OrderNotFoundError(Exception):
    pass

def investigate_order(session: Session, order_number: str) -> dict:
    """
    Retrieve and investigate an order using PostgreSQL.
    This agent is strictly read-only.
    """

    if not order_number or not order_number.strip():
        raise ValueError("Order Number cannot be empty.")

    statement = (
        select(Order).options(selectinload(Order.items)).where(Order.order_number == order_number.strip())
    )

    order = session.exec(statement).first()

    if order is None:
        raise OrderNotFoundError(
            f"Order {order_number} was not found."
        )

    now = datetime.now(timezone.utc)

    is_delayed=order.status.value=="delayed"

    is_overdue = (
        order.expected_delivery is not None
        and order.expected_delivery < now
        and order.status.value != "delivered"
    )

    total_value = sum(
        (item.unit_price * item.quantity for item in order.items), Decimal("0.00"),
    )

    items = [
        {
            "sku":item.product_sku,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
            "line_total": str(item.unit_price * item.quantity),
        }
        for item in order.items
    ]

    return {
        "agent": "order",
        "success": True,
        "order": {
            "id": str(order.id),
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "status": order.status.value,
            "priority": order.priority,
            "order_date": order.order_date.isoformat(),
            "expected_delivery": (
                order.expected_delivery.isoformat()
                if order.expected_delivery
                else None
            ),
            "notes": order.notes,
        },
        "analysis": {
            "is_delayed": is_delayed,
            "is_overdue": is_overdue,
            "item_count": len(items),
            "total_units": sum(
                item["quantity"] for item in items
            ),
            "total_order_value": str(total_value),
        },
        "items":items,
        "investigated_at": now.isoformat(),
    }