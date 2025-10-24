"""add_balance_to_users

Revision ID: 92d746c37098
Revises: 5f8c49130302
Create Date: 2025-10-24 20:42:48.877783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92d746c37098'
down_revision: Union[str, None] = '5f8c49130302'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку balance
    op.add_column('users', sa.Column('balance', sa.Integer(), server_default='0', nullable=False))
    # Добавляем constraint на неотрицательность
    op.create_check_constraint('check_balance_non_negative', 'users', 'balance >= 0')


def downgrade() -> None:
    # Удаляем constraint
    op.drop_constraint('check_balance_non_negative', 'users', type_='check')
    # Удаляем колонку
    op.drop_column('users', 'balance')
