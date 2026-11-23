import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.supplier_product import SupplierProduct


def utc_now():
    return datetime.now(timezone.utc)

class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    supplier_code: str = Field(
        sa_column=Column(String(50), nullable=False, unique=True, index=True)
    )

    name: str = Field(
        max_length=200, nullable=False,
    )

    contact_name: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)

    is_active:bool= Field(default=True, nullable=False)

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    supplier_products: list["SupplierProduct"] = Relationship(
        back_populates="supplier"
    )