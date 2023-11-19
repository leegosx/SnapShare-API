"""Added blacklist table

Revision ID: 641aa3638987
Revises: f2ac1507b9f9
Create Date: 2023-11-19 20:52:35.159823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '641aa3638987'
down_revision: Union[str, None] = 'f2ac1507b9f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklists',
    sa.Column('token', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_blacklists_id'), 'blacklists', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_blacklists_id'), table_name='blacklists')
    op.drop_table('blacklists')
    # ### end Alembic commands ###
