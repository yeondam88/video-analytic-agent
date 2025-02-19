"""fix_segment_embedding_type

Revision ID: fix_segment_embedding_type
Revises: create_search_similar_segments
Create Date: 2024-02-18 17:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'fix_segment_embedding_type'
down_revision: Union[str, None] = 'create_search_similar_segments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop existing function if it exists
    op.execute('DROP FUNCTION IF EXISTS search_similar_segments;')
    
    # Create the updated function with correct types
    op.execute("""
    CREATE OR REPLACE FUNCTION search_similar_segments(
        query_embedding vector(1536),
        match_threshold float DEFAULT 0.7,
        match_count int DEFAULT 5
    )
    RETURNS TABLE (
        id bigint,
        video_id bigint,
        text text,
        start_time double precision,
        end_time double precision,
        speaker_id text,
        similarity double precision,
        metadata jsonb
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            s.id::bigint,
            s.video_id::bigint,
            COALESCE(s.text, '')::text,
            s.start_time::double precision,
            s.end_time::double precision,
            COALESCE(s.speaker_id, '')::text,
            (1 - (s.embedding <=> query_embedding))::double precision as similarity,
            COALESCE(s.metadata, '{}'::jsonb)::jsonb
        FROM
            segments s
        WHERE
            s.embedding IS NOT NULL
            AND s.deleted_at IS NULL
            AND (1 - (s.embedding <=> query_embedding)) >= match_threshold
        ORDER BY
            s.embedding <=> query_embedding
        LIMIT match_count;
    END;
    $$;
    """)
    
    # Create a temporary column for the vector type
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    op.add_column('segments', sa.Column('embedding_vector', Vector(1536), nullable=True))
    
    # Convert existing embeddings to vector type
    op.execute("""
    UPDATE segments 
    SET embedding_vector = embedding::vector 
    WHERE embedding IS NOT NULL;
    """)
    
    # Drop the old column and rename the new one
    op.drop_column('segments', 'embedding')
    op.alter_column('segments', 'embedding_vector', new_column_name='embedding')
    
    # Create an index for similarity search
    op.execute("""
    CREATE INDEX IF NOT EXISTS segments_embedding_idx 
    ON segments 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
    """)

def downgrade() -> None:
    # Drop the updated function
    op.execute('DROP FUNCTION IF EXISTS search_similar_segments;')
    
    # Restore the original function
    op.execute("""
    CREATE OR REPLACE FUNCTION search_similar_segments(
        query_embedding vector(1536),
        match_threshold float DEFAULT 0.7,
        match_count int DEFAULT 5
    )
    RETURNS TABLE (
        id bigint,
        video_id bigint,
        text text,
        start_time double precision,
        end_time double precision,
        speaker_id text,
        similarity double precision,
        metadata jsonb
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            s.id::bigint,
            s.video_id::bigint,
            COALESCE(s.text, '')::text,
            s.start_time::double precision,
            s.end_time::double precision,
            COALESCE(s.speaker_id, '')::text,
            (1 - (s.embedding <=> query_embedding))::double precision as similarity,
            COALESCE(s.metadata, '{}'::jsonb)::jsonb
        FROM
            segments s
        WHERE
            s.embedding IS NOT NULL
            AND s.deleted_at IS NULL
            AND (1 - (s.embedding <=> query_embedding)) >= match_threshold
        ORDER BY
            s.embedding <=> query_embedding
        LIMIT match_count;
    END;
    $$;
    """)
    
    # Create a temporary column for the array type
    op.add_column('segments', sa.Column('embedding_array', sa.ARRAY(sa.Float()), nullable=True))
    
    # Convert vector back to array
    op.execute("""
    UPDATE segments 
    SET embedding_array = embedding::float[] 
    WHERE embedding IS NOT NULL;
    """)
    
    # Drop the vector column and rename the array column
    op.drop_column('segments', 'embedding')
    op.alter_column('segments', 'embedding_array', new_column_name='embedding')
    
    # Drop the index
    op.execute('DROP INDEX IF EXISTS segments_embedding_idx;')