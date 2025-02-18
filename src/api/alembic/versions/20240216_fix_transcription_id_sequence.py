"""Fix transcription id sequence

Revision ID: 20240216_fix_transcription_id
Revises: 20240216_rename_text
Create Date: 2024-02-16 14:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240216_fix_transcription_id'
down_revision: Union[str, None] = '20240216_rename_text'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sequence for transcriptions id
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS transcriptions_id_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;
    """)
    
    # Set the sequence as default for id column
    op.execute("""
        ALTER TABLE transcriptions 
        ALTER COLUMN id SET DEFAULT nextval('transcriptions_id_seq');
    """)
    
    # Set sequence ownership
    op.execute("""
        ALTER SEQUENCE transcriptions_id_seq OWNED BY transcriptions.id;
    """)
    
    # Set current sequence value to max id + 1
    op.execute("""
        SELECT setval('transcriptions_id_seq', 
            COALESCE((SELECT MAX(id) FROM transcriptions), 0) + 1, 
            false);
    """)


def downgrade() -> None:
    # Remove default value from id column
    op.execute("""
        ALTER TABLE transcriptions 
        ALTER COLUMN id DROP DEFAULT;
    """)
    
    # Drop sequence
    op.execute("DROP SEQUENCE IF EXISTS transcriptions_id_seq;") 