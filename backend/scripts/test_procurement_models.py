
from sqlmodel import SQLModel

from app.db.models import (
    Supplier,
    SupplierProduct,
    PurchaseOrder,
    PurchaseOrderStatus,
    PurchaseOrderItem,
)

print("PROCUREMENT MODEL VERIFICATION")

expected_tables = [
    "suppliers",
    "supplier_products",
    "purchase_orders",
    "purchase_order_items",
]

for table_name in expected_tables:
    assert table_name in SQLModel.metadata.tables
    print(f"OK: {table_name}")

# Verify model relationships are registered.
assert hasattr(Supplier, "supplier_products")
assert hasattr(PurchaseOrder, "items")
assert hasattr(PurchaseOrderItem, "purchase_order")

print("\nAll procurement models and relationships loaded successfully.")
