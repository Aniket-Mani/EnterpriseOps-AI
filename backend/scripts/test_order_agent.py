import pytest
from sqlmodel import Session

from app.db.session import engine
from app.agents.order_agent import (
    investigate_order,
    OrderNotFoundError,
)


def test_existing_order():
    with Session(engine) as session:
        result = investigate_order(session, "ORD-1042")

    assert result["success"] is True
    assert result["order"]["order_number"] == "ORD-1042"
    assert len(result["items"]) == 2
    assert result["analysis"]["total_units"] == 8


def test_nonexistent_order():
    with Session(engine) as session:
        with pytest.raises(OrderNotFoundError):
            investigate_order(session, "ORD-9999")


def test_empty_order_number():
    with Session(engine) as session:
        with pytest.raises(ValueError):
            investigate_order(session, "")