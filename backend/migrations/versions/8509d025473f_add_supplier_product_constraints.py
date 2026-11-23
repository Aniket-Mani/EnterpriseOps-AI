
"""add supplier product constraints"""

from typing import Sequence, Union

from alembic import op

# Replace these values with the IDs from your generated file.
revision: str = "8509d025473f"
down_revision: Union[str, Sequence[str], None] = "a615f876be25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_supplier_product_price_nonnegative",
        "supplier_products",
        "unit_price >= 0",
    )

    op.create_check_constraint(
        "ck_supplier_product_lead_time_nonnegative",
        "supplier_products",
        "lead_time_days >= 0",
    )

    op.create_check_constraint(
        "ck_supplier_product_moq_positive",
        "supplier_products",
        "minimum_order_quantity > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_supplier_product_moq_positive",
        "supplier_products",
        type_="check",
    )

    op.drop_constraint(
        "ck_supplier_product_lead_time_nonnegative",
        "supplier_products",
        type_="check",
    )

    op.drop_constraint(
        "ck_supplier_product_price_nonnegative",
        "supplier_products",
        type_="check",
    )
