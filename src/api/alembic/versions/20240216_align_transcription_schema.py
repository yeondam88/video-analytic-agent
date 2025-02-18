"""Align transcription schema with current needs

Revision ID: 20240216_align_transcription
Revises: 20240216_fix_transcription_id
Create Date: 2024-02-16 14:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20240216_align_transcription'
down_revision: Union[str, None] = '20240216_fix_transcription_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename raw_transcript to raw_response and change type to JSONB
    op.alter_column('transcriptions', 'raw_transcript',
        new_column_name='raw_response',
        type_=postgresql.JSONB,
        postgresql_using='raw_transcript::jsonb',
        nullable=False
    )
    
    # Add processed_data column
    op.add_column('transcriptions',
        sa.Column('processed_data', postgresql.JSONB, nullable=True)
    )
    
    # Add extra_data column if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'transcriptions' 
                AND column_name = 'extra_data'
            ) THEN
                ALTER TABLE transcriptions 
                ADD COLUMN extra_data jsonb NOT NULL DEFAULT '{}';
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    # Revert extra_data column
    op.drop_column('transcriptions', 'extra_data')
    
    # Revert processed_data column
    op.drop_column('transcriptions', 'processed_data')
    
    # Revert raw_response back to raw_transcript
    op.alter_column('transcriptions', 'raw_response',
        new_column_name='raw_transcript',
        type_=sa.Text,
        postgresql_using='raw_response::text',
        nullable=False
    ) 