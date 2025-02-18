"""merge multiple heads

Revision ID: ebbeff151687
Revises: add_video_metadata, create_similar_videos_function
Create Date: 2025-02-17 15:52:43.045034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebbeff151687'
down_revision: Union[str, None] = ('add_video_metadata', 'create_similar_videos_function')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
