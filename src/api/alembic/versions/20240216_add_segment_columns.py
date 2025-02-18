"""Add missing columns to segments table

Revision ID: 20240216_add_segment_columns
Revises: 20240216_add_soft_delete
Create Date: 2024-02-16 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '20240216_add_segment_columns'
down_revision: Union[str, None] = '20240216_add_soft_delete'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns
    op.add_column('segments',
                  sa.Column('display_text', sa.Text(), nullable=True))
    op.add_column('segments',
                  sa.Column('title', sa.String(length=255), nullable=True))
    op.add_column('segments',
                  sa.Column('metadata', JSONB, nullable=False, 
                           server_default=sa.text("'{}'::jsonb")))

    # Create index on metadata for performance
    op.create_index(op.f('ix_segments_metadata'), 'segments', ['metadata'], 
                   postgresql_using='gin')


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_segments_metadata'), table_name='segments')
    
    # Drop columns in reverse order
    op.drop_column('segments', 'metadata')
    op.drop_column('segments', 'title')
    op.drop_column('segments', 'display_text') 