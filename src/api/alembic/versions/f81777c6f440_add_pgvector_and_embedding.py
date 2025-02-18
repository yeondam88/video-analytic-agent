"""add_pgvector_and_embedding

Revision ID: f81777c6f440
Revises: 
Create Date: 2025-02-14 18:50:18.521534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f81777c6f440'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Check if segments table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if inspector.has_table('segments'):
        columns = [col['name'] for col in inspector.get_columns('segments')]
        if 'embedding' not in columns:
            # Add embedding column to segments table
            op.add_column('segments', sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True))


def downgrade() -> None:
    # Check if segments table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if inspector.has_table('segments'):
        # Remove embedding column
        op.drop_column('segments', 'embedding')
    
    # Disable pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
