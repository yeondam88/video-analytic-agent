"""fix_id_columns_identity

Revision ID: 3b91103178ad
Revises: 7dd868a731d4
Create Date: 2025-02-16 11:56:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b91103178ad'
down_revision: Union[str, None] = '7dd868a731d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Drop existing default values and add IDENTITY to videos table
    op.execute("""
        ALTER TABLE videos 
        ALTER COLUMN id DROP DEFAULT,
        ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
    """)
    
    # Drop existing default values and add IDENTITY to segments table
    if 'segments' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE segments 
            ALTER COLUMN id DROP DEFAULT,
            ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
        """)
    
    # Drop existing default values and add IDENTITY to summaries table
    if 'summaries' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE summaries 
            ALTER COLUMN id DROP DEFAULT,
            ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
        """)
    
    # Drop existing default values and add IDENTITY to transcriptions table
    if 'transcriptions' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE transcriptions 
            ALTER COLUMN id DROP DEFAULT,
            ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
        """)


def downgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Remove IDENTITY from videos table
    op.execute("""
        ALTER TABLE videos 
        ALTER COLUMN id DROP IDENTITY IF EXISTS,
        ALTER COLUMN id SET DEFAULT nextval('videos_id_seq');
    """)
    
    # Remove IDENTITY from segments table
    if 'segments' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE segments 
            ALTER COLUMN id DROP IDENTITY IF EXISTS,
            ALTER COLUMN id SET DEFAULT nextval('segments_id_seq');
        """)
    
    # Remove IDENTITY from summaries table
    if 'summaries' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE summaries 
            ALTER COLUMN id DROP IDENTITY IF EXISTS,
            ALTER COLUMN id SET DEFAULT nextval('summaries_id_seq');
        """)
    
    # Remove IDENTITY from transcriptions table
    if 'transcriptions' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE transcriptions 
            ALTER COLUMN id DROP IDENTITY IF EXISTS,
            ALTER COLUMN id SET DEFAULT nextval('transcriptions_id_seq');
        """)
