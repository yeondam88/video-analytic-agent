"""merge_videosource_and_status_fixes

Revision ID: cf3b577c9df2
Revises: d40728582443, fdb3daa88e24
Create Date: 2025-02-16 12:46:47.463919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf3b577c9df2'
down_revision: Union[str, None] = ('d40728582443', 'fdb3daa88e24')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
