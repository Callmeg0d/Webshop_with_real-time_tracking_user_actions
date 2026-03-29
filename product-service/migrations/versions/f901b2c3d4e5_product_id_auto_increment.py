"""product_id auto increment (sequence default)

Revision ID: f901b2c3d4e5
Revises: b4c5d6e7f890
Create Date: 2026-02-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f901b2c3d4e5"
down_revision: Union[str, None] = "b4c5d6e7f890"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS products_product_id_seq")
    op.alter_column(
        "products",
        "product_id",
        existing_type=sa.Integer(),
        server_default=sa.text("nextval('products_product_id_seq'::regclass)"),
    )
    op.execute(
        "SELECT setval('products_product_id_seq', COALESCE((SELECT MAX(product_id) FROM products), 1))"
    )


def downgrade() -> None:
    op.alter_column(
        "products",
        "product_id",
        existing_type=sa.Integer(),
        server_default=None,
    )
    op.execute("DROP SEQUENCE IF EXISTS products_product_id_seq")
