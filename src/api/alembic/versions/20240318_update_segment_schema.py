"""Update segments table schema

Revision ID: 20240318_update_segment_schema
Revises: 20240217_update_summaries_table
Create Date: 2024-03-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# revision identifiers, used by Alembic.
revision = '20240318_update_segment_schema'
down_revision = '20240217_update_summaries_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update segments table
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # First convert embedding to float array if it's not already
    op.execute("""
        ALTER TABLE segments 
        ALTER COLUMN embedding TYPE float[] 
        USING CASE 
            WHEN embedding IS NULL THEN NULL 
            WHEN embedding::text = '[]' THEN NULL 
            ELSE embedding::float[] 
        END
    """)
    
    # Then convert to vector type
    op.execute("""
        ALTER TABLE segments 
        ALTER COLUMN embedding TYPE vector(1536) 
        USING embedding::vector(1536)
    """)
    
    # Update other columns
    with op.batch_alter_table('segments') as batch_op:
        batch_op.alter_column('metadata',
            type_=JSONB,
            postgresql_using='CASE WHEN metadata IS NULL THEN NULL ELSE metadata::jsonb END',
            nullable=True)
            
        batch_op.alter_column('title',
            type_=sa.Text,
            nullable=True)
            
        batch_op.alter_column('display_text',
            type_=sa.Text,
            nullable=True)
    
    # Create indexes
    op.execute('CREATE INDEX IF NOT EXISTS segments_metadata_gin_idx ON segments USING gin (metadata)')
    op.execute('CREATE INDEX IF NOT EXISTS segments_embedding_idx ON segments USING ivfflat (embedding vector_cosine_ops)')


def downgrade() -> None:
    # Remove indexes
    op.execute('DROP INDEX IF EXISTS segments_metadata_gin_idx')
    op.execute('DROP INDEX IF EXISTS segments_embedding_idx')
    
    # First convert vector back to float array
    op.execute("""
        ALTER TABLE segments 
        ALTER COLUMN embedding TYPE float[] 
        USING embedding::float[]
    """)
    
    # Update other columns
    with op.batch_alter_table('segments') as batch_op:
        batch_op.alter_column('metadata',
            type_=sa.JSON,
            postgresql_using='metadata::json',
            nullable=True)
            
        batch_op.alter_column('title',
            type_=sa.String,
            nullable=True)
            
        batch_op.alter_column('display_text',
            type_=sa.String,
            nullable=True) 