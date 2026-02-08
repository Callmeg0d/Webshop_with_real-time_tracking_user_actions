"""Add order_saga_reservations table

Revision ID: b2c45650c001
Revises: ab34549ebefd
Create Date: 2026-02-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c45650c001"
down_revision: Union[str, None] = "ab34549ebefd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "order_saga_reservations",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("stock_done", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("balance_done", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("order_id"),
    )


def downgrade() -> None:
    op.drop_table("order_saga_reservations")
