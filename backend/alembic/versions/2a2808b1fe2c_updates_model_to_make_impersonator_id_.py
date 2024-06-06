"""updates model to make impersonator_id optional

Revision ID: 2a2808b1fe2c
Revises: a0e635e2ccf0
Create Date: 2024-06-05 17:59:08.222267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a2808b1fe2c'
down_revision: Union[str, None] = 'a0e635e2ccf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
