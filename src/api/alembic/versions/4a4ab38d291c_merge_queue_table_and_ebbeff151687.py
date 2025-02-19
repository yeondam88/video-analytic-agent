"""merge queue_table and ebbeff151687

Revision ID: 4a4ab38d291c
Revises: create_queue_table, ebbeff151687
Create Date: 2025-02-18 00:21:20.934366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a4ab38d291c'
down_revision: Union[str, None] = ('create_queue_table', 'ebbeff151687')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
