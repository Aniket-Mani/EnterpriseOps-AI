import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Numeric, String, Integer, UniqueConstraint,
)
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.supplier import Supplier


def utc_now():
    return datetime.now(timezone.utc)

class SupplierProduct(SQLModel, table=True):
    __tablename__ = "supplier_products"

    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "product_sku",
            name="uq_supplier_product_sku",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_supplier_product_price_nonnegative",
        ),
        CheckConstraint(
            "lead_time_days >= 0",
            name="ck_supplier_product_lead_time_nonnegative",
        ),
        CheckConstraint(
            "minimum_order_quantity > 0",
            name="ck_supplier_product_moq_positive",
        ),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    supplier_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("suppliers.id", ondelete="CASCADE"),nullable=False,index=True,)
    )

    product_sku: str = Field(
        sa_column=Column(String(50), nullable=False, index=True)
    )

    product_name: str = Field( max_length=200, nullable=False,)

    unit_price: Decimal = Field(
        sa_type=Numeric(12, 2), nullable=False,
    )

    lead_time_days: int = Field(
        default=7, ge=0, nullable=False,
    )

    minimum_order_quantity: int = Field(
        default=1, ge=1, nullable=False,
    )

    is_available: bool = Field(default=True, nullable=False)

    last_updated: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    supplier: "Supplier" = Relationship(
        back_populates="supplier_products"
    )

