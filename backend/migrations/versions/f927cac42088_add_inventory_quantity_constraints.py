
"""add inventory quantity constraints

Revision ID: f927cac42088
Revises: d881dbffd64f
"""

from typing import Sequence, Union

from alembic import op

revision: str = "f927cac42088"
down_revision: Union[str, Sequence[str], None] = "d881dbffd64f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_inventory_quantity_on_hand_nonnegative",
        "inventory",
        "quantity_on_hand >= 0",
    )

    op.create_check_constraint(
        "ck_inventory_quantity_reserved_nonnegative",
        "inventory",
        "quantity_reserved >= 0",
    )

    op.create_check_constraint(
        "ck_inventory_reserved_not_above_on_hand",
        "inventory",
        "quantity_reserved <= quantity_on_hand",
    )


def downgrade() -> None:
    pass
