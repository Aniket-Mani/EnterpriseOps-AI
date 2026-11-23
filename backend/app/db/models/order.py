import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column,DateTime, Enum as SAEnum, String
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.order_item import OrderItem
    
def utc_now():
    return datetime.now(timezone.utc)

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    DELAYED = "delayed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(SQLModel, table = True):
    __tablename__="orders"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key= True,
    )

    order_number: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False,)
    )

    customer_name: str = Field(
        max_length=150, nullable=False,
    )

    status: OrderStatus = Field(
        default= OrderStatus.PENDING,
        sa_column=Column(SAEnum(OrderStatus,name="order_status",values_callable=lambda enum:[e.value for e in enum],),nullable=False, index=True,),
    )

    priority: str = Field(
        default="normal", max_length=20, nullable=False,
    )

    order_date: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    expected_delivery: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    notes: str | None = Field(default=None, nullable=True)

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    items: list["OrderItem"] = Relationship(back_populates="order")

