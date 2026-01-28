"""Change image column to text slug

Revision ID: change_image_to_text_slug
Revises: da2cdaa94518
Create Date: 2026-01-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "change_image_to_text_slug"
down_revision: Union[str, None] = "da2cdaa94518"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "products",
        "image",
        existing_type=sa.Integer(),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "products",
        "image",
        existing_type=sa.Text(),
        type_=sa.Integer(),
        existing_nullable=True,
    )

