"""Add soft delete to segments

Revision ID: 20240216_add_soft_delete
Revises: 20240216_fix_transcription_id
Create Date: 2024-02-16 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240216_add_soft_delete'
down_revision: Union[str, None] = '20240216_fix_transcription_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add deleted_at column to segments table
    op.add_column('segments',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Add index for faster soft delete queries
    op.create_index(
        'ix_segments_deleted_at',
        'segments',
        ['deleted_at']
    )


def downgrade() -> None:
    # Remove index first
    op.drop_index('ix_segments_deleted_at')
    
    # Remove deleted_at column
    op.drop_column('segments', 'deleted_at') 