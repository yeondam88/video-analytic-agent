"""add_video_progress_and_result_fields

Revision ID: 0f85d7255bb5
Revises: 9aa919142ce2
Create Date: 2025-02-15 23:45:03.590000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0f85d7255bb5'
down_revision: Union[str, None] = '9aa919142ce2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns
    columns = [col['name'] for col in inspector.get_columns('videos')]
    
    # Add progress tracking columns if they don't exist
    if 'progress' not in columns:
        op.add_column('videos', sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'))
    if 'steps_completed' not in columns:
        op.add_column('videos', sa.Column('steps_completed', postgresql.ARRAY(sa.String()), nullable=True))
    if 'error' not in columns:
        op.add_column('videos', sa.Column('error', sa.String(), nullable=True))
    
    # Handle transcript column conversion if it exists
    if 'transcript' in columns:
        op.execute('ALTER TABLE videos ALTER COLUMN transcript TYPE JSON USING CASE WHEN transcript IS NULL THEN NULL ELSE transcript::json END')
    
    # Add new result columns if they don't exist
    if 'embeddings' not in columns:
        op.add_column('videos', sa.Column('embeddings', postgresql.JSON(), nullable=True))
    if 'summary' not in columns:
        op.add_column('videos', sa.Column('summary', postgresql.JSON(), nullable=True))
    
    # Add indices if they don't exist
    if not inspector.get_indexes('videos'):
        op.create_index(op.f('ix_videos_id'), 'videos', ['id'], unique=False)
    if not inspector.get_indexes('segments'):
        op.create_index(op.f('ix_segments_id'), 'segments', ['id'], unique=False)
    if not inspector.get_indexes('summaries'):
        op.create_index(op.f('ix_summaries_id'), 'summaries', ['id'], unique=False)


def downgrade() -> None:
    # Drop indices
    op.drop_index(op.f('ix_summaries_id'), table_name='summaries')
    op.drop_index(op.f('ix_segments_id'), table_name='segments')
    op.drop_index(op.f('ix_videos_id'), table_name='videos')
    
    # Convert transcript back to TEXT
    op.execute('ALTER TABLE videos ALTER COLUMN transcript TYPE TEXT USING transcript::text')
    
    # Drop columns
    op.drop_column('videos', 'summary')
    op.drop_column('videos', 'embeddings')
    op.drop_column('videos', 'error')
    op.drop_column('videos', 'steps_completed')
    op.drop_column('videos', 'progress')
