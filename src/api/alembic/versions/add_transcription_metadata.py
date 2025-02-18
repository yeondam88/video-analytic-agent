"""add transcription metadata

Revision ID: add_transcription_metadata
Revises: 11a70293b6c8
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_transcription_metadata'
down_revision = '11a70293b6c8'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add metadata column to transcriptions table
    op.add_column('transcriptions', sa.Column('metadata', JSONB, nullable=True))
    
    # Add index for faster queries on detected_language
    op.create_index(
        'ix_transcriptions_detected_language',
        'transcriptions',
        [sa.text("(metadata->>'detected_language')")],
        postgresql_using='btree'
    )

def downgrade() -> None:
    # Remove index first
    op.drop_index('ix_transcriptions_detected_language')
    
    # Remove metadata column
    op.drop_column('transcriptions', 'metadata') 