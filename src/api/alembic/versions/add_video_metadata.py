"""add video metadata

Revision ID: add_video_metadata
Revises: add_transcription_metadata
Create Date: 2024-03-21 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_video_metadata'
down_revision = 'add_transcription_metadata'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add metadata column to videos table
    op.add_column('videos', sa.Column('metadata', JSONB, nullable=True))
    
    # Create indexes for common metadata queries
    op.create_index(
        'ix_videos_metadata_summary',
        'videos',
        [sa.text("(metadata->>'summary')")],
        postgresql_using='btree'
    )
    
    op.create_index(
        'ix_videos_metadata_title',
        'videos',
        [sa.text("(metadata->>'title')")],
        postgresql_using='btree'
    )

def downgrade() -> None:
    # Remove indexes first
    op.drop_index('ix_videos_metadata_summary')
    op.drop_index('ix_videos_metadata_title')
    
    # Remove metadata column
    op.drop_column('videos', 'metadata') 