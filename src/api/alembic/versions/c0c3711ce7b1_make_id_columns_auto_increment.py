"""make_id_columns_auto_increment

Revision ID: c0c3711ce7b1
Revises: 770d1292dfae
Create Date: 2025-02-16 00:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0c3711ce7b1'
down_revision: Union[str, None] = '770d1292dfae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add IDENTITY to videos table
    op.execute("""
        ALTER TABLE videos 
        ALTER COLUMN id DROP DEFAULT,
        ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
    """)
    
    # Add IDENTITY to segments table
    if 'segments' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE segments 
            ALTER COLUMN id DROP DEFAULT,
            ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
        """)
    
    # Add IDENTITY to summaries table
    if 'summaries' in inspector.get_table_names():
        op.execute("""
            ALTER TABLE summaries 
            ALTER COLUMN id DROP DEFAULT,
            ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
        """)
    
    # Add IDENTITY to transcriptions table
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
