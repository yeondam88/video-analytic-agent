"""add_video_progress_fields_v2

Revision ID: 9aa919142ce2
Revises: 20240318_enable_vector_and_rls
Create Date: 2025-02-15 23:35:12.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9aa919142ce2'
down_revision: Union[str, None] = '20240318_enable_vector_and_rls'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('videos')]
    
    # Add new columns for progress tracking if they don't exist
    if 'progress' not in existing_columns:
        op.add_column('videos', sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'))
    if 'steps_completed' not in existing_columns:
        op.add_column('videos', sa.Column('steps_completed', postgresql.ARRAY(sa.String()), nullable=True))
    if 'error' not in existing_columns:
        op.add_column('videos', sa.Column('error', sa.String(), nullable=True))
    
    # Add new columns for results if they don't exist
    if 'transcript' not in existing_columns:
        op.add_column('videos', sa.Column('transcript', sa.Text(), nullable=True))
    if 'embeddings' not in existing_columns:
        op.add_column('videos', sa.Column('embeddings', postgresql.JSON(), nullable=True))
    if 'summary' not in existing_columns:
        op.add_column('videos', sa.Column('summary', postgresql.JSON(), nullable=True))
    
    # Check if enum types exist before creating them
    existing_enums = [e['name'] for e in inspector.get_enums()]
    
    if 'videosource' not in existing_enums:
        op.execute("CREATE TYPE videosource AS ENUM ('LOOM', 'YOUTUBE')")
    if 'videostatus' not in existing_enums:
        op.execute("CREATE TYPE videostatus AS ENUM ('PENDING', 'DOWNLOADING', 'DOWNLOADED', 'EXTRACTING_AUDIO', 'AUDIO_EXTRACTED', 'TRANSCRIBING', 'TRANSCRIBED', 'FAILED')")
    
    # Add source and status columns directly with the new enum types
    if 'source' not in existing_columns:
        op.execute("ALTER TABLE videos ADD COLUMN source videosource NOT NULL DEFAULT 'LOOM'")
    if 'status' not in existing_columns:
        op.execute("ALTER TABLE videos ADD COLUMN status videostatus NOT NULL DEFAULT 'PENDING'")


def downgrade() -> None:
    # Drop new columns
    op.drop_column('videos', 'transcript')
    op.drop_column('videos', 'embeddings')
    op.drop_column('videos', 'summary')
    op.drop_column('videos', 'progress')
    op.drop_column('videos', 'steps_completed')
    op.drop_column('videos', 'error')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS videosource')
    op.execute('DROP TYPE IF EXISTS videostatus')
