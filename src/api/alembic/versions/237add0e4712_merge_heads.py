"""merge heads

Revision ID: 237add0e4712
Revises: 0550ada9378a, add_transcription_metadata
Create Date: 2025-02-17 15:02:08.992522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '237add0e4712'
down_revision: Union[str, None] = ('0550ada9378a', 'add_transcription_metadata')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
