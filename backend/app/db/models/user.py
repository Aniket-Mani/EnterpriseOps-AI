import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel

def utc_now():
    return datetime.now(timezone.utc)

class User(SQLModel, table = True):
    __tablename__ = "users"

    id:uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    email: str = Field(
        sa_column=Column(String(255),unique=True, index=True, nullable=False,)
    )

    full_name: str = Field(
        max_length=150, nullable=False,
    )

    role: str = Field(
        default="operator", max_length=50, nullable = False,
    )

    is_active: bool = Field(
        default=True, nullable=False,
    )
    
    hashed_password: str = Field(max_length=255, nullable=False)

    created_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable = False),
    )
    
    updated_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable = False),
    )
