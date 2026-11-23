import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, DateTime,ForeignKey,Integer, String, UniqueConstraint,CheckConstraint
)
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.warehouse import Warehouse

def utc_now():
    return datetime.now(timezone.utc)

class Inventory(SQLModel, table = True):
    __tablename__ = "inventory"

    __table_args__ = (
        CheckConstraint(
            "quantity_on_hand >= 0",
            name="ck_inventory_quantity_on_hand_nonnegative",
        ),
        CheckConstraint(
            "quantity_reserved >= 0",
            name="ck_inventory_quantity_reserved_nonnegative",
        ),
        CheckConstraint(
            "quantity_reserved <= quantity_on_hand",
            name="ck_inventory_reserved_not_above_on_hand",
        ),
        UniqueConstraint(
            "warehouse_id", "product_sku", name="uq_inventory_warehouse_sku",
        ),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key= True,
    )

    warehouse_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False,index=True, )
    )

    product_sku: str = Field(
        sa_column=Column(String(50), nullable=False, index=True)
    )

    product_name: str = Field(
        max_length=200, nullable=False,
    )

    quantity_on_hand: int = Field(
        default=0, ge=0, nullable=False,
    )

    quantity_reserved: int = Field(
        default=0,ge=0,nullable=False,
    )

    reorder_level: int = Field(
        default=10, ge=0, nullable=False,
    )

    last_updated: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    warehouse: "Warehouse" = Relationship( back_populates="inventory_records" )

    @property
    def available_quantity(self) -> int:
        return self.quantity_on_hand - self.quantity_reserved

