"""removes impersonator id from user

Revision ID: fcf3dbedfd77
Revises: 2a2808b1fe2c
Create Date: 2024-06-06 14:00:45.464950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcf3dbedfd77'
down_revision: Union[str, None] = '2a2808b1fe2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
