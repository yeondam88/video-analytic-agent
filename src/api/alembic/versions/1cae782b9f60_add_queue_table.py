"""add queue table

Revision ID: 1cae782b9f60
Revises: create_similar_videos_function
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1cae782b9f60'
down_revision = 'create_similar_videos_function'
branch_labels = None
depends_on = None

def upgrade():
    # Create queue_items table
    op.create_table(
        'queue_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('queue_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('video_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')",
            name='queue_status_check'
        )
    )
    
    # Create indexes
    op.create_index(op.f('ix_queue_items_status'), 'queue_items', ['status'], unique=False)
    op.create_index(op.f('ix_queue_items_priority'), 'queue_items', ['priority'], unique=False)
    op.create_index(op.f('ix_queue_items_created_at'), 'queue_items', ['created_at'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_queue_items_created_at'), table_name='queue_items')
    op.drop_index(op.f('ix_queue_items_priority'), table_name='queue_items')
    op.drop_index(op.f('ix_queue_items_status'), table_name='queue_items')
    
    # Drop table
    op.drop_table('queue_items')
