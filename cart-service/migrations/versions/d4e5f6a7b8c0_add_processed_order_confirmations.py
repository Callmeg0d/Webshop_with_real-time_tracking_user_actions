"""add processed_order_confirmations

Revision ID: d4e5f6a7b8c0
Revises: bf4621b8a9d5
Create Date: 2026-03-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c0"
down_revision: Union[str, None] = "bf4621b8a9d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "processed_order_confirmations",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "processed_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("order_id"),
    )


def downgrade() -> None:
    op.drop_table("processed_order_confirmations")
