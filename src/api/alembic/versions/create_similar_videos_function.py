"""create similar videos function

Revision ID: create_similar_videos_function
Revises: 237add0e4712
Create Date: 2024-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'create_similar_videos_function'
down_revision = '237add0e4712'
branch_labels = None
depends_on = None

def upgrade():
    # Create the function for finding similar videos
    op.execute("""
    CREATE OR REPLACE FUNCTION get_similar_videos(
        exclude_video_id text,
        match_threshold float DEFAULT 0.7,  -- Increased default threshold to 0.7 (70% similarity)
        match_count int DEFAULT 5
    )
    RETURNS TABLE (
        id bigint,
        title text,
        url text,
        source_id text,
        similarity float,
        segment_count int,  -- Added to help understand match quality
        avg_confidence float  -- Added to help understand match quality
    )
    AS $$
    WITH target_embedding AS (
        SELECT 
            AVG(CAST(embedding AS vector(1536)))::vector(1536) as avg_embedding,
            COUNT(*) as segment_count,
            AVG((metadata->>'confidence')::float) as avg_confidence
        FROM segments
        WHERE video_id::text = exclude_video_id
        AND deleted_at IS NULL
        GROUP BY video_id
    ),
    avg_embeddings AS (
        SELECT 
            video_id,
            AVG(CAST(embedding AS vector(1536)))::vector(1536) as avg_embedding,
            COUNT(*) as segment_count,
            AVG((metadata->>'confidence')::float) as avg_confidence
        FROM segments
        WHERE video_id::text != exclude_video_id
        AND deleted_at IS NULL
        GROUP BY video_id
    )
    SELECT DISTINCT 
        v.id,
        v.title,
        v.url,
        v.source_id,
        1 - (ae.avg_embedding <=> (SELECT avg_embedding FROM target_embedding)) as similarity,
        ae.segment_count,
        ae.avg_confidence
    FROM avg_embeddings ae
    JOIN videos v ON v.id = ae.video_id::int
    WHERE v.status = 'COMPLETED'
    AND (1 - (ae.avg_embedding <=> (SELECT avg_embedding FROM target_embedding))) > match_threshold
    AND ae.segment_count >= 3  -- Only include videos with at least 3 segments
    AND ae.avg_confidence >= 0.7  -- Only include videos with high confidence transcriptions
    ORDER BY similarity DESC
    LIMIT match_count;
    $$ LANGUAGE SQL STABLE;
    """)

def downgrade():
    # Drop the function
    op.execute("DROP FUNCTION IF EXISTS get_similar_videos(text, float, int);") 