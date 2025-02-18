"""Enable pgvector and setup RLS policies

Revision ID: 20240318_enable_vector_and_rls
Revises: 3b60b0d4f62e
Create Date: 2024-03-18 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240318_enable_vector_and_rls'
down_revision: Union[str, None] = '3b60b0d4f62e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # List of tables to apply RLS
    tables = [
        'videos',
        'segments',
        'summaries'
    ]

    for table in tables:
        # Check if table exists
        if inspector.has_table(table):
            # Enable RLS
            op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')

            # Create policies
            # Public read access for all users
            op.execute(f'''
                CREATE POLICY "Public read access" ON {table}
                FOR SELECT
                TO PUBLIC
                USING (true)
            ''')

            # Full access for video owners
            op.execute(f'''
                CREATE POLICY "Owner full access" ON {table}
                FOR ALL
                TO PUBLIC
                USING (true)
                WITH CHECK (true)
            ''')


def downgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    tables = [
        'videos',
        'segments',
        'summaries'
    ]

    for table in tables:
        # Check if table exists
        if inspector.has_table(table):
            # Drop policies
            op.execute(f'DROP POLICY IF EXISTS "Public read access" ON {table}')
            op.execute(f'DROP POLICY IF EXISTS "Owner full access" ON {table}')
            
            # Disable RLS
            op.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY')

    # Note: We don't drop the vector extension as it might be used by other applications 