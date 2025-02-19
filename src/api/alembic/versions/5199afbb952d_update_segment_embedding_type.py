"""update_segment_embedding_type

Revision ID: 5199afbb952d
Revises: 4a4ab38d291c
Create Date: 2025-02-18 01:11:15.662413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5199afbb952d'
down_revision: Union[str, None] = '4a4ab38d291c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table to store embeddings
    op.execute("""
    CREATE TEMPORARY TABLE temp_embeddings AS 
    SELECT id, regexp_replace(embedding::text, '[\\[\\]]', '', 'g') as embedding
    FROM segments;
    """)

    # Drop the existing embedding column
    op.drop_column('segments', 'embedding')

    # Add the new embedding column
    op.add_column('segments', sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True))

    # Update the embedding column from the temporary table
    op.execute("""
    UPDATE segments s
    SET embedding = string_to_array(t.embedding, ',')::float[]
    FROM temp_embeddings t
    WHERE s.id = t.id;
    """)

    # Drop the temporary table
    op.execute('DROP TABLE temp_embeddings;')


def downgrade() -> None:
    # Create a temporary table to store embeddings
    op.execute("""
    CREATE TEMPORARY TABLE temp_embeddings AS 
    SELECT id, array_to_string(embedding, ',') as embedding
    FROM segments;
    """)

    # Drop the existing embedding column
    op.drop_column('segments', 'embedding')

    # Add the vector column back
    op.add_column('segments', sa.Column('embedding', Vector(1536), nullable=True))

    # Update the embedding column from the temporary table
    op.execute("""
    UPDATE segments s
    SET embedding = ('['||t.embedding||']')::vector
    FROM temp_embeddings t
    WHERE s.id = t.id;
    """)

    # Drop the temporary table
    op.execute('DROP TABLE temp_embeddings;')
