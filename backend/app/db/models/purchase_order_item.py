
import uuid
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Numeric,
    String,
)
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.purchase_order import PurchaseOrder


class PurchaseOrderItem(SQLModel, table=True):
    __tablename__ = "purchase_order_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_purchase_order_item_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_purchase_order_item_price_nonnegative",
        ),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    purchase_order_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("purchase_orders.id", ondelete="CASCADE"),nullable=False,index=True,)
    )

    product_sku: str = Field(
        sa_column=Column(String(50), nullable=False, index=True)
    )

    product_name: str = Field(
        max_length=200,nullable=False,
    )

    quantity: int = Field(
        gt=0,nullable=False,
    )

    unit_price: Decimal = Field(
        sa_column=Column(Numeric(12, 2), nullable=False)
    )

    purchase_order: "PurchaseOrder" = Relationship(back_populates="items")
