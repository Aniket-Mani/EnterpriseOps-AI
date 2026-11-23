import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.purchase_order_item import PurchaseOrderItem

def utc_now():
    return datetime.now(timezone.utc)


class PurchaseOrderStatus(str, Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    ordered = "ordered"
    partially_received = "partially_received"
    received = "received"
    cancelled = "cancelled"


class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_orders"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    po_number: str = Field(
        sa_column=Column( String(50),nullable=False,unique=True,index=True,)
    )

    supplier_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("suppliers.id", ondelete="RESTRICT"),nullable=False,index=True, )
    )

    status: PurchaseOrderStatus = Field(
        default=PurchaseOrderStatus.draft, nullable=False,
    )

    order_date: datetime | None = Field(default=None)

    expected_delivery: datetime | None = Field(default=None)

    notes: str | None = Field(default=None, max_length=1000)

    created_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    updated_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    items: list["PurchaseOrderItem"] = Relationship( back_populates="purchase_order")
