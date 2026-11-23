
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.db.session import engine
from app.db.models import Order, OrderItem, OrderStatus


now = datetime.now(timezone.utc)

orders_data = [
    {
        "order_number": "ORD-1042",
        "customer_name": "Acme Manufacturing",
        "status": OrderStatus.DELAYED,
        "priority": "high",
        "order_date": now - timedelta(days=8),
        "expected_delivery": now - timedelta(days=2),
        "notes": "Delayed due to a suspected supplier shortage.",
        "items": [
            ("SKU-1001", "Industrial Motor", 5, Decimal("450.00")),
            ("SKU-1002", "Control Unit", 3, Decimal("275.00")),
        ],
    },
    {
        "order_number": "ORD-1043",
        "customer_name": "Northstar Retail",
        "status": OrderStatus.PROCESSING,
        "priority": "normal",
        "order_date": now - timedelta(days=2),
        "expected_delivery": now + timedelta(days=5),
        "notes": "Standard order processing.",
        "items": [
            ("SKU-1003", "Power Adapter", 10, Decimal("25.00")),
        ],
    },
    {
        "order_number": "ORD-1044",
        "customer_name": "Vertex Solutions",
        "status": OrderStatus.CONFIRMED,
        "priority": "normal",
        "order_date": now - timedelta(days=1),
        "expected_delivery": now + timedelta(days=7),
        "notes": "Confirmed and awaiting fulfillment.",
        "items": [
            ("SKU-1001", "Industrial Motor", 2, Decimal("450.00")),
            ("SKU-1004", "Sensor Module", 4, Decimal("80.00")),
        ],
    },
]


def seed_orders():
    with Session(engine) as session:
        for data in orders_data:
            existing = session.exec(
                select(Order).where(
                    Order.order_number == data["order_number"]
                )
            ).first()

            if existing:
                print(f"Skipping existing order: {data['order_number']}")
                continue

            order = Order(
                order_number=data["order_number"],
                customer_name=data["customer_name"],
                status=data["status"],
                priority=data["priority"],
                order_date=data["order_date"],
                expected_delivery=data["expected_delivery"],
                notes=data["notes"],
            )

            session.add(order)
            session.flush()

            for sku, name, quantity, price in data["items"]:
                session.add(
                    OrderItem(
                        order_id=order.id,
                        product_sku=sku,
                        product_name=name,
                        quantity=quantity,
                        unit_price=price,
                    )
                )

            print(f"Created order: {data['order_number']}")

        session.commit()
        print("\nOrder seeding completed.")


if __name__ == "__main__":
    seed_orders()
