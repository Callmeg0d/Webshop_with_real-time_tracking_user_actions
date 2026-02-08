"""Add idempotency_keys table

Revision ID: b4c5d6e7f890
Revises: change_image_to_text_slug
Create Date: 2026-02-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4c5d6e7f890"
down_revision: Union[str, None] = "change_image_to_text_slug"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key_type", sa.String(64), nullable=False),
        sa.Column("business_key", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_type", "business_key", name="uq_idempotency_key_type_business"),
    )


def downgrade() -> None:
    op.drop_table("idempotency_keys")
