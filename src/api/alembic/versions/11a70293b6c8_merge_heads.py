"""merge heads

Revision ID: 11a70293b6c8
Revises: 3b4c2d1e, 20240321_add_processing_details
Create Date: 2025-02-16 13:45:29.594754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11a70293b6c8'
down_revision: Union[str, None] = ('3b4c2d1e', '20240321_add_processing_details')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
