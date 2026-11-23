
import uuid
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Numeric, String
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.order import Order
    

class OrderItem(SQLModel, table = True):
    __tablename__="order_items"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    order_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True,)
    )

    product_sku: str = Field(
        sa_column=Column(String(50), nullable=False, index=True)
    )

    product_name: str = Field(
        max_length=200, nullable= False,
    )

    quantity: int = Field(
        gt=0,nullable=False,
    )

    unit_price: Decimal = Field(
        sa_column=Column(Numeric(12,2), nullable= False)
    )

    order: "Order" = Relationship(back_populates="items")
