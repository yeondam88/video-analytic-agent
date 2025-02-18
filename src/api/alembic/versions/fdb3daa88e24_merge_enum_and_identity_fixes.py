"""merge_enum_and_identity_fixes

Revision ID: fdb3daa88e24
Revises: 3b91103178ad, 62b0823ba349
Create Date: 2025-02-16 12:36:55.594633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdb3daa88e24'
down_revision: Union[str, None] = ('3b91103178ad', '62b0823ba349')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
