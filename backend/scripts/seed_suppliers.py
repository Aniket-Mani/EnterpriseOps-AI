
from decimal import Decimal

from sqlmodel import Session, select

from app.db.session import engine
from app.db.models import Supplier, SupplierProduct


SUPPLIERS = [
    {
        "supplier_code": "SUP-001",
        "name": "Apex Industrial Supplies",
    },
    {
        "supplier_code": "SUP-002",
        "name": "Global Components Ltd",
    },
    {
        "supplier_code": "SUP-003",
        "name": "Prime Manufacturing Co",
    },
]


SUPPLIER_PRODUCTS = [
    # Apex Industrial Supplies
    {
        "supplier_code": "SUP-001",
        "sku": "SKU-1001",
        "name": "Industrial Motor",
        "price": Decimal("430.00"),
        "lead_time": 7,
        "moq": 1,
        "available": True,
    },
    {
        "supplier_code": "SUP-001",
        "sku": "SKU-1002",
        "name": "Control Unit",
        "price": Decimal("260.00"),
        "lead_time": 8,
        "moq": 2,
        "available": True,
    },

    # Global Components Ltd
    {
        "supplier_code": "SUP-002",
        "sku": "SKU-1001",
        "name": "Industrial Motor",
        "price": Decimal("450.00"),
        "lead_time": 4,
        "moq": 1,
        "available": True,
    },
    {
        "supplier_code": "SUP-002",
        "sku": "SKU-1002",
        "name": "Control Unit",
        "price": Decimal("275.00"),
        "lead_time": 5,
        "moq": 1,
        "available": True,
    },

    # Prime Manufacturing Co
    {
        "supplier_code": "SUP-003",
        "sku": "SKU-1001",
        "name": "Industrial Motor",
        "price": Decimal("410.00"),
        "lead_time": 12,
        "moq": 5,
        "available": True,
    },
    {
        "supplier_code": "SUP-003",
        "sku": "SKU-1002",
        "name": "Control Unit",
        "price": Decimal("250.00"),
        "lead_time": 10,
        "moq": 5,
        "available": False,
    },
]


def seed_suppliers():
    with Session(engine) as session:
        suppliers_by_code = {}

        for supplier_data in SUPPLIERS:
            supplier = session.exec(
                select(Supplier).where(
                    Supplier.supplier_code == supplier_data["supplier_code"]
                )
            ).first()

            if supplier is None:
                supplier = Supplier(**supplier_data)
                session.add(supplier)
                print(f"Created supplier: {supplier_data['name']}")
            else:
                print(f"Supplier already exists: {supplier_data['name']}")

            suppliers_by_code[supplier_data["supplier_code"]] = supplier

        session.flush()

        for product_data in SUPPLIER_PRODUCTS:
            supplier = suppliers_by_code[product_data["supplier_code"]]

            existing = session.exec(
                select(SupplierProduct).where(
                    SupplierProduct.supplier_id == supplier.id,
                    SupplierProduct.product_sku == product_data["sku"],
                )
            ).first()

            if existing is not None:
                print(
                    f"Supplier product already exists: "
                    f"{product_data['supplier_code']} - "
                    f"{product_data['sku']}"
                )
                continue

            supplier_product = SupplierProduct(
                supplier_id=supplier.id,
                product_sku=product_data["sku"],
                product_name=product_data["name"],
                unit_price=product_data["price"],
                lead_time_days=product_data["lead_time"],
                minimum_order_quantity=product_data["moq"],
                is_available=product_data["available"],
            )

            session.add(supplier_product)

            print(
                f"Added {product_data['sku']} for "
                f"{product_data['supplier_code']}"
            )

        session.commit()
        print("\nSupplier seeding completed successfully.")


if __name__ == "__main__":
    seed_suppliers()
