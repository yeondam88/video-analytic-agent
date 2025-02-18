"""add processing details

Revision ID: 20240321_add_processing_details
Revises: 458d35582e6d
Create Date: 2024-03-21 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '20240321_add_processing_details'
down_revision = '458d35582e6d'
branch_labels = None
depends_on = None

def upgrade():
    # Create a temporary table to store existing data
    op.execute("""
        CREATE TABLE videos_temp AS 
        SELECT * FROM videos;
    """)
    
    # Drop the old table
    op.execute("DROP TABLE videos")
    
    # Create the new table with the processing_details column
    op.execute("""
        CREATE TABLE videos (
            id INTEGER PRIMARY KEY,
            source VARCHAR NOT NULL,
            source_id VARCHAR NOT NULL,
            url VARCHAR NOT NULL,
            title VARCHAR,
            description VARCHAR,
            duration INTEGER,
            status VARCHAR NOT NULL,
            thumbnail_url VARCHAR,
            progress FLOAT NOT NULL DEFAULT 0.0,
            steps_completed VARCHAR[] NOT NULL DEFAULT '{}',
            error VARCHAR,
            transcript JSONB,
            embeddings JSONB,
            summary JSONB,
            extra_data JSONB NOT NULL DEFAULT '{}',
            processing_details JSONB NOT NULL DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Copy data from temporary table
    op.execute("""
        INSERT INTO videos (
            id, source, source_id, url, title, description, duration,
            status, thumbnail_url, progress, steps_completed, error,
            transcript, embeddings, summary, extra_data, created_at, updated_at
        )
        SELECT 
            id, source, source_id, url, title, description, duration,
            status, thumbnail_url, 
            COALESCE(progress, 0.0) as progress,
            COALESCE(steps_completed, '{}') as steps_completed,
            error,
            transcript, embeddings, summary, 
            COALESCE(extra_data, '{}') as extra_data,
            created_at, updated_at
        FROM videos_temp;
    """)
    
    # Drop temporary table
    op.execute("DROP TABLE videos_temp")

def downgrade():
    # Create a temporary table without processing_details
    op.execute("""
        CREATE TABLE videos_temp AS 
        SELECT 
            id, source, source_id, url, title, description, duration,
            status, thumbnail_url, progress, steps_completed, error,
            transcript, embeddings, summary, extra_data, created_at, updated_at
        FROM videos;
    """)
    
    # Drop the current table
    op.execute("DROP TABLE videos")
    
    # Create the table without processing_details
    op.execute("""
        CREATE TABLE videos (
            id INTEGER PRIMARY KEY,
            source VARCHAR NOT NULL,
            source_id VARCHAR NOT NULL,
            url VARCHAR NOT NULL,
            title VARCHAR,
            description VARCHAR,
            duration INTEGER,
            status VARCHAR NOT NULL,
            thumbnail_url VARCHAR,
            progress FLOAT NOT NULL DEFAULT 0.0,
            steps_completed VARCHAR[] NOT NULL DEFAULT '{}',
            error VARCHAR,
            transcript JSONB,
            embeddings JSONB,
            summary JSONB,
            extra_data JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Copy data back
    op.execute("""
        INSERT INTO videos (
            id, source, source_id, url, title, description, duration,
            status, thumbnail_url, progress, steps_completed, error,
            transcript, embeddings, summary, extra_data, created_at, updated_at
        )
        SELECT 
            id, source, source_id, url, title, description, duration,
            status, thumbnail_url, 
            COALESCE(progress, 0.0) as progress,
            COALESCE(steps_completed, '{}') as steps_completed,
            error,
            transcript, embeddings, summary, 
            COALESCE(extra_data, '{}') as extra_data,
            created_at, updated_at
        FROM videos_temp;
    """)
    
    # Drop temporary table
    op.execute("DROP TABLE videos_temp") 