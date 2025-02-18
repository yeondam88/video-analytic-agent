"""fix_steps_completed_column_type

Revision ID: 458d35582e6d
Revises: cf3b577c9df2
Create Date: 2025-02-16 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '458d35582e6d'
down_revision: Union[str, None] = 'cf3b577c9df2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table to store the data
    op.execute("""
        CREATE TEMP TABLE videos_temp AS 
        SELECT id, source, source_id, url, title, description, duration, 
               status, thumbnail_url, progress, error, transcript, embeddings, 
               summary, extra_data, created_at, updated_at
        FROM videos;
    """)
    
    # Drop the existing table
    op.execute("DROP TABLE videos CASCADE;")
    
    # Create the table with the correct column type
    op.execute("""
        CREATE TABLE videos (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source videosource NOT NULL,
            source_id VARCHAR NOT NULL,
            url VARCHAR NOT NULL,
            title VARCHAR,
            description VARCHAR,
            duration INTEGER,
            status videostatus NOT NULL,
            thumbnail_url VARCHAR,
            progress FLOAT NOT NULL DEFAULT 0.0,
            steps_completed VARCHAR[] DEFAULT ARRAY[]::VARCHAR[],
            error VARCHAR,
            transcript JSONB,
            embeddings JSONB,
            summary JSONB,
            extra_data JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)
    
    # Restore the data
    op.execute("""
        INSERT INTO videos (
            source, source_id, url, title, description, duration, 
            status, thumbnail_url, progress, error, transcript, embeddings, 
            summary, extra_data, created_at, updated_at
        )
        SELECT 
            source, source_id, url, title, description, duration,
            status, thumbnail_url, progress, error, transcript, embeddings,
            summary, extra_data, created_at, updated_at
        FROM videos_temp;
    """)
    
    # Drop the temporary table
    op.execute("DROP TABLE videos_temp;")


def downgrade() -> None:
    # This is a fix migration, downgrading would reintroduce the bug
    raise NotImplementedError("Downgrade is not supported for this migration")
