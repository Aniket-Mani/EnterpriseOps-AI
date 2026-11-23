import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.inventory import Inventory

class Warehouse(SQLModel, table = True):
    __tablename__="warehouses"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    warehouse_code: str = Field(
        max_length=50,unique=True,index=True,nullable=False,
    )

    name: str = Field(
        max_length=150, nullable=False,
    )

    location: str = Field(
        max_length=255, nullable=False,
    )

    is_active: bool = Field(
        default=True, nullable=False,
    )

    inventory_records: list["Inventory"] = Relationship(
        back_populates="warehouse"
    )