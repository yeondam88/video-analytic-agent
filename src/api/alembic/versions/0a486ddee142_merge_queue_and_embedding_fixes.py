"""merge_queue_and_embedding_fixes

Revision ID: 0a486ddee142
Revises: 1cae782b9f60, fix_segment_embedding_type
Create Date: 2025-02-19 19:42:36.867218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a486ddee142'
down_revision: Union[str, None] = ('1cae782b9f60', 'fix_segment_embedding_type')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
