"""Add extra_data to transcriptions

Revision ID: 3b4c2d1e
Revises: 20240318_create_initial_tables
Create Date: 2024-03-18 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3b4c2d1e'
down_revision: Union[str, None] = '20240318_create_initial_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add extra_data column to transcriptions table
    op.add_column('transcriptions',
        sa.Column('extra_data', postgresql.JSONB, nullable=False, server_default='{}')
    )


def downgrade() -> None:
    # Remove extra_data column from transcriptions table
    op.drop_column('transcriptions', 'extra_data') 