"""create_search_similar_segments_function

Revision ID: create_search_similar_segments
Revises: 9e4cfb3c36b0
Create Date: 2024-02-18 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'create_search_similar_segments'
down_revision: Union[str, None] = '9e4cfb3c36b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create function for searching similar segments using pgvector
    op.execute("""
    CREATE OR REPLACE FUNCTION search_similar_segments(
        query_embedding vector(1536),
        match_threshold float DEFAULT 0.7,
        match_count int DEFAULT 5
    )
    RETURNS TABLE (
        id int,
        video_id int,
        text text,
        start_time float,
        end_time float,
        speaker_id text,
        similarity float,
        metadata jsonb
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            s.id,
            s.video_id::int,
            s.text,
            s.start_time::float,
            s.end_time::float,
            s.speaker_id,
            1 - (s.embedding <=> query_embedding) as similarity,
            s.metadata
        FROM
            segments s
        WHERE
            s.embedding IS NOT NULL
            AND s.deleted_at IS NULL
        ORDER BY
            s.embedding <=> query_embedding
        LIMIT match_count;
    END;
    $$;
    """)

def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS search_similar_segments;") 