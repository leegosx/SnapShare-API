"""Rename image counter

Revision ID: ddac46760df6
Revises: ffb99e576208
Create Date: 2023-11-15 16:01:58.342887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddac46760df6'
down_revision: Union[str, None] = 'ffb99e576208'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('uploaded_images', sa.Integer(), nullable=True))
    op.drop_column('users', 'image_count')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('image_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('users', 'uploaded_images')
    # ### end Alembic commands ###
