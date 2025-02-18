"""add_extra_data_columns

Revision ID: 770d1292dfae
Revises: 0f85d7255bb5
Create Date: 2025-02-16 00:19:02.723066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '770d1292dfae'
down_revision: Union[str, None] = '0f85d7255bb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add extra_data column to videos table
    if 'videos' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('videos')]
        if 'extra_data' not in columns:
            op.add_column('videos', sa.Column('extra_data', postgresql.JSONB(), server_default='{}', nullable=False))
    
    # Add extra_data column to segments table
    if 'segments' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('segments')]
        if 'extra_data' not in columns:
            op.add_column('segments', sa.Column('extra_data', postgresql.JSONB(), server_default='{}', nullable=False))
    
    # Add extra_data column to transcriptions table
    if 'transcriptions' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('transcriptions')]
        if 'extra_data' not in columns:
            op.add_column('transcriptions', sa.Column('extra_data', postgresql.JSONB(), server_default='{}', nullable=False))
    
    # Add extra_data column to summaries table
    if 'summaries' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('summaries')]
        if 'extra_data' not in columns:
            op.add_column('summaries', sa.Column('extra_data', postgresql.JSONB(), server_default='{}', nullable=False))


def downgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Remove extra_data columns from all tables
    tables = ['videos', 'segments', 'transcriptions', 'summaries']
    for table in tables:
        if table in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns(table)]
            if 'extra_data' in columns:
                op.drop_column(table, 'extra_data')
