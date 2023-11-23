"""Added blacklist table

Revision ID: fe4d15949783
Revises: e15b47a6bcab
Create Date: 2023-11-16 13:55:08.089575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fe4d15949783'
down_revision: Union[str, None] = 'e15b47a6bcab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "blacklist",
        sa.Column("token", sa.String, unique=True),
        sa.Column("email", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("blacklist")
