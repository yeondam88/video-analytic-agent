"""fix_videosource_enum

Revision ID: d40728582443
Revises: 3b91103178ad
Create Date: 2024-03-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd40728582443'
down_revision: Union[str, None] = '3b91103178ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table to store the data
    op.execute("""
        CREATE TABLE videos_temp AS 
        SELECT 
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source::text as source,
            status, extra_data
        FROM videos
    """)

    # Drop dependent tables if they exist
    op.execute("""
        DROP TABLE IF EXISTS video_segments CASCADE;
        DROP TABLE IF EXISTS video_chapters CASCADE;
    """)

    # Drop the videos table
    op.execute("""
        DROP TABLE videos CASCADE
    """)

    # Drop the old enum type
    op.execute("""
        DROP TYPE IF EXISTS videosource CASCADE;
    """)

    # Create the new enum type with all required values
    op.execute("""
        CREATE TYPE videosource AS ENUM ('LOOM', 'YOUTUBE', 'LOCAL');
    """)

    # Create the videos table with the new enum
    op.execute("""
        CREATE TABLE videos (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source_id VARCHAR(255),
            url TEXT,
            title TEXT,
            description TEXT,
            duration INTEGER,
            thumbnail_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            progress FLOAT DEFAULT 0,
            steps_completed INTEGER DEFAULT 0,
            error TEXT,
            transcript JSONB,
            embeddings JSONB,
            summary JSONB,
            source videosource NOT NULL,
            status videostatus NOT NULL DEFAULT 'PENDING',
            extra_data JSONB
        )
    """)

    # First, create a temporary table with the transformed data
    op.execute("""
        CREATE TEMPORARY TABLE transformed_data AS
        SELECT 
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            COALESCE(transcript::jsonb, '{}'::jsonb) as transcript, 
            COALESCE(embeddings::jsonb, '{}'::jsonb) as embeddings, 
            COALESCE(summary::jsonb, '{}'::jsonb) as summary,
            CASE source
                WHEN 'LOOM' THEN 'LOOM'::videosource
                WHEN 'YOUTUBE' THEN 'YOUTUBE'::videosource
                WHEN 'LOCAL' THEN 'LOCAL'::videosource
                ELSE 'LOOM'::videosource
            END as source,
            status,
            COALESCE(extra_data::jsonb, '{}'::jsonb) as extra_data
        FROM videos_temp
    """)

    # Then insert from the transformed data
    op.execute("""
        INSERT INTO videos (
            source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source, status, extra_data
        )
        SELECT 
            source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source, status, extra_data
        FROM transformed_data
    """)

    # Drop temporary tables
    op.execute("DROP TABLE videos_temp")


def downgrade() -> None:
    # This is a fix migration, downgrading would reintroduce the bug
    raise NotImplementedError("Downgrade not supported for this migration.")
