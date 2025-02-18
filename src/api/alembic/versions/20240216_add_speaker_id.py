"""Add speaker_id to segments table

Revision ID: 20240216_add_speaker_id
Revises: 20240216_add_segment_columns
Create Date: 2024-02-16 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240216_add_speaker_id'
down_revision: Union[str, None] = '20240216_add_segment_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add speaker_id column to segments table
    op.add_column('segments',
                  sa.Column('speaker_id', sa.String(), nullable=True))
    
    # Create index for faster speaker lookups
    op.create_index(op.f('ix_segments_speaker_id'), 'segments', ['speaker_id'])


def downgrade() -> None:
    # Drop index first
    op.drop_index(op.f('ix_segments_speaker_id'), table_name='segments')
    
    # Drop speaker_id column
    op.drop_column('segments', 'speaker_id') 