"""update_video_status_enum

Revision ID: 7dd868a731d4
Revises: c0c3711ce7b1
Create Date: 2024-02-16 08:33:07.182726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7dd868a731d4'
down_revision: Union[str, None] = 'c0c3711ce7b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create temporary tables to store existing data
    op.execute("""
        CREATE TABLE videos_temp AS 
        SELECT id, source_id, url, title, description, duration, thumbnail_url, 
               created_at, updated_at, progress, steps_completed, 
               error, transcript, embeddings, summary, source, 
               status::text as status, extra_data
        FROM videos
    """)

    # Store segments, summaries, and transcriptions data
    op.execute("""
        CREATE TABLE segments_temp AS 
        SELECT id, video_id, start_time, end_time, text, embedding, created_at, updated_at
        FROM segments
    """)
    op.execute("""
        CREATE TABLE summaries_temp AS 
        SELECT id, video_id, text, created_at, updated_at
        FROM summaries
    """)
    op.execute("""
        CREATE TABLE transcriptions_temp AS 
        SELECT id, video_id, text, created_at, updated_at
        FROM transcriptions
    """)

    # Drop dependent tables first
    op.execute("DROP TABLE transcriptions")
    op.execute("DROP TABLE segments")
    op.execute("DROP TABLE summaries")

    # Now we can drop the videos table
    op.execute("DROP TABLE videos")

    # Create new enum type
    op.execute("""
        CREATE TYPE video_status_new AS ENUM (
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
        )
    """)

    # Create new videos table with updated status enum
    op.execute("""
        CREATE TABLE videos (
            id INTEGER NOT NULL,
            source_id VARCHAR NOT NULL,
            url VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            description VARCHAR,
            duration FLOAT,
            thumbnail_url VARCHAR,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            progress FLOAT NOT NULL DEFAULT 0.0,
            steps_completed VARCHAR[],
            error VARCHAR,
            transcript TEXT,
            embeddings JSONB,
            summary JSONB,
            source videosource NOT NULL DEFAULT 'LOOM',
            status video_status_new NOT NULL DEFAULT 'PENDING',
            extra_data JSONB,
            PRIMARY KEY (id)
        )
    """)

    # Restore data from temp table
    op.execute("""
        INSERT INTO videos (
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source, status, extra_data
        )
        SELECT 
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source::videosource,
            CASE
                WHEN status = 'PENDING' THEN 'PENDING'::video_status_new
                WHEN status = 'DOWNLOADING' THEN 'DOWNLOADING'::video_status_new
                WHEN status = 'DOWNLOADED' THEN 'DOWNLOADED'::video_status_new
                WHEN status = 'EXTRACTING_AUDIO' THEN 'EXTRACTING_AUDIO'::video_status_new
                WHEN status = 'AUDIO_EXTRACTED' THEN 'AUDIO_EXTRACTED'::video_status_new
                WHEN status = 'TRANSCRIBING' THEN 'TRANSCRIBING'::video_status_new
                WHEN status = 'TRANSCRIBED' THEN 'TRANSCRIBED'::video_status_new
                WHEN status = 'FAILED' THEN 'FAILED'::video_status_new
                ELSE 'PENDING'::video_status_new
            END,
            extra_data
        FROM videos_temp
    """)

    # Create new segments table
    op.execute("""
        CREATE TABLE segments (
            id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            start_time FLOAT NOT NULL,
            end_time FLOAT NOT NULL,
            text VARCHAR NOT NULL,
            embedding FLOAT[],
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(video_id) REFERENCES videos (id)
        )
    """)

    # Create new summaries table
    op.execute("""
        CREATE TABLE summaries (
            id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            text VARCHAR NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(video_id) REFERENCES videos (id)
        )
    """)

    # Create new transcriptions table
    op.execute("""
        CREATE TABLE transcriptions (
            id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            text VARCHAR NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(video_id) REFERENCES videos (id)
        )
    """)

    # Restore data from temp tables
    op.execute("""
        INSERT INTO segments (
            id, video_id, start_time, end_time, text, embedding, created_at, updated_at
        )
        SELECT 
            id, video_id, start_time, end_time, text, embedding, created_at, updated_at
        FROM segments_temp
    """)
    op.execute("""
        INSERT INTO summaries (
            id, video_id, text, created_at, updated_at
        )
        SELECT 
            id, video_id, text, created_at, updated_at
        FROM summaries_temp
    """)
    op.execute("""
        INSERT INTO transcriptions (
            id, video_id, text, created_at, updated_at
        )
        SELECT 
            id, video_id, text, created_at, updated_at
        FROM transcriptions_temp
    """)

    # Drop temporary tables
    op.execute("DROP TABLE videos_temp")
    op.execute("DROP TABLE segments_temp")
    op.execute("DROP TABLE summaries_temp")
    op.execute("DROP TABLE transcriptions_temp")

    # Drop old enum type
    op.execute("DROP TYPE IF EXISTS videostatus")


def downgrade() -> None:
    # Create old enum type
    op.execute("""
        CREATE TYPE videostatus AS ENUM (
            'PENDING',
            'DOWNLOADING',
            'DOWNLOADED',
            'EXTRACTING_AUDIO',
            'AUDIO_EXTRACTED',
            'TRANSCRIBING',
            'TRANSCRIBED',
            'FAILED'
        )
    """)

    # Create a temporary table to store existing data
    op.execute("""
        CREATE TABLE videos_temp AS 
        SELECT id, source_id, url, title, description, duration, thumbnail_url,
               created_at, updated_at, progress, steps_completed, error,
               transcript, embeddings, summary, source, status::text as status,
               extra_data
        FROM videos
    """)

    # Store segments, summaries, and transcriptions data
    op.execute("""
        CREATE TABLE segments_temp AS 
        SELECT id, video_id, start_time, end_time, text, embedding, created_at, updated_at
        FROM segments
    """)
    op.execute("""
        CREATE TABLE summaries_temp AS 
        SELECT id, video_id, text, created_at, updated_at
        FROM summaries
    """)
    op.execute("""
        CREATE TABLE transcriptions_temp AS 
        SELECT id, video_id, text, created_at, updated_at
        FROM transcriptions
    """)

    # Drop dependent tables first
    op.execute("DROP TABLE transcriptions")
    op.execute("DROP TABLE segments")
    op.execute("DROP TABLE summaries")

    # Now we can drop the videos table
    op.execute("DROP TABLE videos")

    # Create new videos table with old status enum
    op.execute("""
        CREATE TABLE videos (
            id INTEGER NOT NULL,
            source_id VARCHAR NOT NULL,
            url VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            description VARCHAR,
            duration FLOAT,
            thumbnail_url VARCHAR,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            progress FLOAT NOT NULL DEFAULT 0.0,
            steps_completed VARCHAR[],
            error VARCHAR,
            transcript TEXT,
            embeddings JSONB,
            summary JSONB,
            source videosource NOT NULL DEFAULT 'LOOM',
            status videostatus NOT NULL DEFAULT 'PENDING',
            extra_data JSONB,
            PRIMARY KEY (id)
        )
    """)

    # Restore data from temp table
    op.execute("""
        INSERT INTO videos (
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source, status, extra_data
        )
        SELECT 
            id, source_id, url, title, description, duration, thumbnail_url,
            created_at, updated_at, progress, steps_completed, error,
            transcript, embeddings, summary, source::videosource,
            CASE
                WHEN status = 'PENDING' THEN 'PENDING'::videostatus
                WHEN status = 'DOWNLOADING' THEN 'DOWNLOADING'::videostatus
                WHEN status = 'DOWNLOADED' THEN 'DOWNLOADED'::videostatus
                WHEN status = 'EXTRACTING_AUDIO' THEN 'EXTRACTING_AUDIO'::videostatus
                WHEN status = 'AUDIO_EXTRACTED' THEN 'AUDIO_EXTRACTED'::videostatus
                WHEN status = 'TRANSCRIBING' THEN 'TRANSCRIBING'::videostatus
                WHEN status = 'TRANSCRIBED' THEN 'TRANSCRIBED'::videostatus
                WHEN status = 'FAILED' THEN 'FAILED'::videostatus
                ELSE 'PENDING'::videostatus
            END,
            extra_data
        FROM videos_temp
    """)

    # Create new segments table
    op.execute("""
        CREATE TABLE segments (
            id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            start_time FLOAT NOT NULL,
            end_time FLOAT NOT NULL,
            text VARCHAR NOT NULL,
            embedding FLOAT[],
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(video_id) REFERENCES videos (id)
        )
    """)

    # Create new summaries table
    op.execute("""
        CREATE TABLE summaries (
            id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            text VARCHAR NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(video_id) REFERENCES videos (id)
        )
    """)

    # Create new transcriptions table
    op.execute("""
        CREATE TABLE transcriptions (
            id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            text VARCHAR NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(video_id) REFERENCES videos (id)
        )
    """)

    # Restore data from temp tables
    op.execute("""
        INSERT INTO segments (
            id, video_id, start_time, end_time, text, embedding, created_at, updated_at
        )
        SELECT 
            id, video_id, start_time, end_time, text, embedding, created_at, updated_at
        FROM segments_temp
    """)
    op.execute("""
        INSERT INTO summaries (
            id, video_id, text, created_at, updated_at
        )
        SELECT 
            id, video_id, text, created_at, updated_at
        FROM summaries_temp
    """)
    op.execute("""
        INSERT INTO transcriptions (
            id, video_id, text, created_at, updated_at
        )
        SELECT 
            id, video_id, text, created_at, updated_at
        FROM transcriptions_temp
    """)

    # Drop temporary tables
    op.execute("DROP TABLE videos_temp")
    op.execute("DROP TABLE segments_temp")
    op.execute("DROP TABLE summaries_temp")
    op.execute("DROP TABLE transcriptions_temp")

    # Drop new enum type
    op.execute("DROP TYPE IF EXISTS video_status_new")
