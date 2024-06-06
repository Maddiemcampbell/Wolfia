"""adds impersonator id

Revision ID: a0e635e2ccf0
Revises: 3216d8119800
Create Date: 2024-06-05 16:52:58.570572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0e635e2ccf0'
down_revision: Union[str, None] = '3216d8119800'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
