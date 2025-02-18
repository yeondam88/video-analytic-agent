"""Rename text column to raw_transcript

Revision ID: 20240216_rename_text
Revises: 20240216_add_raw_transcript
Create Date: 2024-02-16 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240216_rename_text'
down_revision: Union[str, None] = '20240216_add_raw_transcript'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table with the new schema
    op.execute("""
        CREATE TABLE transcriptions_temp AS 
        SELECT id, video_id, text as raw_transcript, extra_data, created_at, updated_at
        FROM transcriptions;
    """)
    
    # Drop the old table
    op.execute("DROP TABLE transcriptions")
    
    # Create the new table with the correct schema
    op.execute("""
        CREATE TABLE transcriptions (
            id INTEGER PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            raw_transcript TEXT NOT NULL,
            extra_data JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Copy data from temporary table
    op.execute("""
        INSERT INTO transcriptions (id, video_id, raw_transcript, extra_data, created_at, updated_at)
        SELECT id, video_id, raw_transcript, extra_data, created_at, updated_at
        FROM transcriptions_temp;
    """)
    
    # Drop temporary table
    op.execute("DROP TABLE transcriptions_temp")


def downgrade() -> None:
    # Create a temporary table with the old schema
    op.execute("""
        CREATE TABLE transcriptions_temp AS 
        SELECT id, video_id, raw_transcript as text, extra_data, created_at, updated_at
        FROM transcriptions;
    """)
    
    # Drop the new table
    op.execute("DROP TABLE transcriptions")
    
    # Create the old table with the original schema
    op.execute("""
        CREATE TABLE transcriptions (
            id INTEGER PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            text TEXT NOT NULL,
            extra_data JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Copy data back
    op.execute("""
        INSERT INTO transcriptions (id, video_id, text, extra_data, created_at, updated_at)
        SELECT id, video_id, text, extra_data, created_at, updated_at
        FROM transcriptions_temp;
    """)
    
    # Drop temporary table
    op.execute("DROP TABLE transcriptions_temp") 