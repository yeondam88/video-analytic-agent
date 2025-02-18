"""merge_heads

Revision ID: 3b60b0d4f62e
Revises: f81777c6f440, 20240318_create_initial_tables
Create Date: 2025-02-15 23:07:38.490018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b60b0d4f62e'
down_revision: Union[str, None] = ('f81777c6f440', '20240318_create_initial_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tables first
    op.get_bind().execute(sa.text('SELECT 1'))


def downgrade() -> None:
    pass
