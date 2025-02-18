"""Add raw_transcript column to transcriptions

Revision ID: 20240216_add_raw_transcript
Revises: 11a70293b6c8
Create Date: 2024-02-16 14:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240216_add_raw_transcript'
down_revision: Union[str, None] = '11a70293b6c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add raw_transcript column to transcriptions table
    op.add_column('transcriptions',
        sa.Column('raw_transcript', sa.Text(), nullable=False, server_default='')
    )


def downgrade() -> None:
    # Remove raw_transcript column from transcriptions table
    op.drop_column('transcriptions', 'raw_transcript') 