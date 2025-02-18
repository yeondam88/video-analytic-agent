"""merge_heads

Revision ID: 04a62f02a10d
Revises: 20240216_align_transcription, 20240318_update_segment_schema
Create Date: 2025-02-17 13:36:26.802357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04a62f02a10d'
down_revision: Union[str, None] = ('20240216_align_transcription', '20240318_update_segment_schema')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
