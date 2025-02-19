"""update_segment_embedding_type_v2

Revision ID: 9e4cfb3c36b0
Revises: 5199afbb952d
Create Date: 2024-02-18 01:21:22.060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '9e4cfb3c36b0'
down_revision: Union[str, None] = '5199afbb952d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table to store embeddings
    op.execute('''
    CREATE TEMPORARY TABLE temp_embeddings AS 
    SELECT id, array_to_string(embedding::float[], ',') as embedding
    FROM segments;
    ''')

    # Drop the existing embedding column
    op.drop_column('segments', 'embedding')

    # Add the new embedding column
    op.add_column('segments', sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True))

    # Update the embedding column from the temporary table
    op.execute('''
    UPDATE segments s
    SET embedding = string_to_array(t.embedding, ',')::float[]
    FROM temp_embeddings t
    WHERE s.id = t.id;
    ''')

    # Drop the temporary table
    op.execute('DROP TABLE temp_embeddings;')


def downgrade() -> None:
    # Create a temporary table to store embeddings
    op.execute('''
    CREATE TEMPORARY TABLE temp_embeddings AS 
    SELECT id, array_to_string(embedding, ',') as embedding
    FROM segments;
    ''')

    # Drop the existing embedding column
    op.drop_column('segments', 'embedding')

    # Add the vector column back
    op.add_column('segments', sa.Column('embedding', Vector(1536), nullable=True))

    # Update the embedding column from the temporary table
    op.execute('''
    UPDATE segments s
    SET embedding = string_to_array(t.embedding, ',')::float[]::vector
    FROM temp_embeddings t
    WHERE s.id = t.id;
    ''')

    # Drop the temporary table
    op.execute('DROP TABLE temp_embeddings;')
