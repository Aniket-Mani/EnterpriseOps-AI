
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.db.session import engine
from app.db.models import Warehouse, Inventory


WAREHOUSES = [
    {
        "warehouse_code": "WH-CHN-01",
        "name": "Chennai Central Warehouse",
        "location": "Chennai, Tamil Nadu",
    },
    {
        "warehouse_code": "WH-BLR-01",
        "name": "Bangalore Distribution Center",
        "location": "Bangalore, Karnataka",
    },
]

STOCK = {
    "WH-CHN-01": [
        ("SKU-1001", "Industrial Motor", 2, 0, 5),
        ("SKU-1002", "Control Unit", 10, 2, 5),
        ("SKU-1003", "Power Adapter", 50, 5, 10),
        ("SKU-1004", "Sensor Module", 20, 2, 5),
    ],
    "WH-BLR-01": [
        ("SKU-1001", "Industrial Motor", 8, 1, 5),
        ("SKU-1002", "Control Unit", 1, 0, 5),
        ("SKU-1003", "Power Adapter", 30, 3, 10),
        ("SKU-1004", "Sensor Module", 12, 2, 5),
    ],
}


def seed_inventory():
    with Session(engine) as session:

        warehouses = {}

        for data in WAREHOUSES:
            warehouse = session.exec(
                select(Warehouse).where(
                    Warehouse.warehouse_code == data["warehouse_code"]
                )
            ).first()

            if warehouse is None:
                warehouse = Warehouse(**data)
                session.add(warehouse)
                session.flush()
                print(f"Created warehouse: {warehouse.warehouse_code}")
            else:
                print(f"Using existing warehouse: {warehouse.warehouse_code}")

            warehouses[data["warehouse_code"]] = warehouse

        for warehouse_code, products in STOCK.items():
            warehouse = warehouses[warehouse_code]

            for sku, name, on_hand, reserved, reorder in products:
                existing = session.exec(
                    select(Inventory).where(
                        Inventory.warehouse_id == warehouse.id,
                        Inventory.product_sku == sku,
                    )
                ).first()

                if existing:
                    print(f"Skipping existing stock: {warehouse_code} / {sku}")
                    continue

                session.add(
                    Inventory(
                        warehouse_id=warehouse.id,
                        product_sku=sku,
                        product_name=name,
                        quantity_on_hand=on_hand,
                        quantity_reserved=reserved,
                        reorder_level=reorder,
                        last_updated=datetime.now(timezone.utc),
                    )
                )

                print(f"Added stock: {warehouse_code} / {sku}")

        session.commit()
        print("\nInventory seeding completed.")


if __name__ == "__main__":
    seed_inventory()
