"""fix video status enum

Revision ID: 62b0823ba349
Revises: 7dd868a731d4
Create Date: 2024-02-16 12:36:42.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '62b0823ba349'
down_revision: Union[str, None] = '7dd868a731d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table to store the data with status as text
    op.execute("""
        CREATE TABLE videos_temp AS 
        SELECT 
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, 
            CASE 
                WHEN steps_completed IS NULL THEN 0
                ELSE array_length(steps_completed, 1)
            END as steps_completed,
            error,
            transcript, embeddings, summary, source,
            status::text as status,
            extra_data
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

    # Drop the old enum types
    op.execute("""
        DROP TYPE IF EXISTS videostatus CASCADE;
        DROP TYPE IF EXISTS videosource CASCADE;
    """)

    # Create the new enum types
    op.execute("""
        CREATE TYPE videosource AS ENUM ('YOUTUBE', 'LOCAL');
        CREATE TYPE videostatus AS ENUM (
            'PENDING',
            'DOWNLOADING',
            'DOWNLOADED',
            'EXTRACTING_AUDIO',
            'AUDIO_EXTRACTED',
            'TRANSCRIBING',
            'TRANSCRIBED',
            'SEGMENTING',
            'PROCESSING',
            'COMPLETED',
            'FAILED'
        );
    """)

    # Create the videos table with the new enum
    op.execute("""
        CREATE TABLE videos (
            id SERIAL PRIMARY KEY,
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
            'YOUTUBE'::videosource as source,
            CASE status
                WHEN 'PENDING' THEN 'PENDING'::videostatus
                WHEN 'DOWNLOADING' THEN 'DOWNLOADING'::videostatus
                WHEN 'DOWNLOADED' THEN 'DOWNLOADED'::videostatus
                WHEN 'EXTRACTING_AUDIO' THEN 'EXTRACTING_AUDIO'::videostatus
                WHEN 'AUDIO_EXTRACTED' THEN 'AUDIO_EXTRACTED'::videostatus
                WHEN 'TRANSCRIBING' THEN 'TRANSCRIBING'::videostatus
                WHEN 'TRANSCRIBED' THEN 'TRANSCRIBED'::videostatus
                WHEN 'SEGMENTING' THEN 'SEGMENTING'::videostatus
                WHEN 'PROCESSING' THEN 'PROCESSING'::videostatus
                WHEN 'COMPLETED' THEN 'COMPLETED'::videostatus
                WHEN 'FAILED' THEN 'FAILED'::videostatus
                ELSE 'PENDING'::videostatus
            END as status,
            COALESCE(extra_data::jsonb, '{}'::jsonb) as extra_data
        FROM videos_temp
    """)

    # Then insert from the transformed data
    op.execute("""
        INSERT INTO videos (
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source, status, extra_data
        )
        SELECT * FROM transformed_data
    """)

    # Drop the temporary tables
    op.execute("""
        DROP TABLE transformed_data;
        DROP TABLE videos_temp;
    """)


def downgrade() -> None:
    # This is a fix migration, we don't want to reintroduce the bug
    pass
