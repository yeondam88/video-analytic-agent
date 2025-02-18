"""Update summaries table

Revision ID: 20240217_update_summaries_table
Revises: 20240216_add_speaker_id
Create Date: 2024-02-17 11:35:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20240217_update_summaries_table'
down_revision: Union[str, None] = '20240216_add_speaker_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename text column to content
    op.alter_column('summaries', 'text',
                    new_column_name='content',
                    existing_type=sa.String(),
                    nullable=False)
    
    # Add summary_type column
    op.add_column('summaries',
                  sa.Column('summary_type', sa.String(), nullable=False, server_default='transcript'))
    
    # Add extra_data column if it doesn't exist
    op.add_column('summaries',
                  sa.Column('extra_data', sa.JSON(), nullable=False, server_default='{}'))


def downgrade() -> None:
    # Drop extra_data column
    op.drop_column('summaries', 'extra_data')
    
    # Drop summary_type column
    op.drop_column('summaries', 'summary_type')
    
    # Rename content column back to text
    op.alter_column('summaries', 'content',
                    new_column_name='text',
                    existing_type=sa.String(),
                    nullable=False) 