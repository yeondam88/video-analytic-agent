"""add raw_response and processed_data columns

Revision ID: 0550ada9378a
Revises: 04a62f02a10d
Create Date: 2024-03-18 21:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0550ada9378a'
down_revision: Union[str, None] = '04a62f02a10d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old table and sequence
    op.execute("DROP TABLE IF EXISTS transcriptions")
    op.execute("DROP SEQUENCE IF EXISTS transcriptions_id_seq")
    
    # Create sequence for id
    op.execute("CREATE SEQUENCE transcriptions_id_seq")
    
    # Create the new table with the correct schema
    op.execute("""
        CREATE TABLE transcriptions (
            id INTEGER PRIMARY KEY DEFAULT nextval('transcriptions_id_seq'),
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            raw_response JSONB NOT NULL,
            processed_data JSONB,
            extra_data JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)


def downgrade() -> None:
    # Drop the new table and sequence
    op.execute("DROP TABLE IF EXISTS transcriptions")
    op.execute("DROP SEQUENCE IF EXISTS transcriptions_id_seq")
    
    # Create sequence for id
    op.execute("CREATE SEQUENCE transcriptions_id_seq")
    
    # Create the old table with the original schema
    op.execute("""
        CREATE TABLE transcriptions (
            id INTEGER PRIMARY KEY DEFAULT nextval('transcriptions_id_seq'),
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            text TEXT NOT NULL,
            extra_data JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
