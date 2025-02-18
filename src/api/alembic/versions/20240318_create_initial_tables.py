"""Create initial tables

Revision ID: 20240318_create_initial_tables
Revises: f81777c6f440
Create Date: 2024-03-18 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20240318_create_initial_tables'
down_revision: Union[str, None] = 'f81777c6f440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Drop dependent tables first if they exist
    if inspector.has_table('transcriptions'):
        op.drop_table('transcriptions', schema=None)
    if inspector.has_table('summaries'):
        op.drop_table('summaries', schema=None)
    if inspector.has_table('segments'):
        op.drop_table('segments', schema=None)
    if inspector.has_table('videos'):
        op.drop_table('videos', schema=None)

    # Create enum types if they don't exist
    inspector = sa.inspect(conn)
    
    # Check if enums exist
    existing_enums = [e['name'] for e in inspector.get_enums()]
    
    if 'video_source' not in existing_enums:
        op.execute("CREATE TYPE video_source AS ENUM ('LOOM', 'YOUTUBE', 'LOCAL')")
    
    if 'video_status' not in existing_enums:
        op.execute("""
            CREATE TYPE video_status AS ENUM (
                'PENDING',
                'DOWNLOADING',
                'PROCESSING',
                'TRANSCRIBING',
                'SEGMENTING',
                'COMPLETED',
                'FAILED'
            )
        """)

    # Create tables in the correct order
    op.create_table('videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('steps_completed', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('segments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('transcriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('transcriptions')
    op.drop_table('summaries')
    op.drop_table('segments')
    op.drop_table('videos')
    
    # Drop enums if they exist
    existing_enums = [e['name'] for e in inspector.get_enums()]
    
    if 'video_status' in existing_enums:
        op.execute('DROP TYPE video_status')
    if 'video_source' in existing_enums:
        op.execute('DROP TYPE video_source') 