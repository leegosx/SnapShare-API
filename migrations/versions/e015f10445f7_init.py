"""'Init'

Revision ID: e015f10445f7
Revises: 
Create Date: 2023-11-14 23:16:40.913809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e015f10445f7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    if not sa.inspect(op.get_bind()).has_table('tags'):
        op.create_table('tags',
            sa.Column('name', sa.String(), nullable=True),
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
        op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)

    # Repeat the similar check for each table
    if not sa.inspect(op.get_bind()).has_table('users'):
        op.create_table('users',
            # ... columns definitions ...
        )
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Continue for 'images', 'comments', and 'image_m2m_tags' tables

    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # The downgrade script should ideally mirror the upgrade script
    # Check for table existence before dropping tables

    if sa.inspect(op.get_bind()).has_table('image_m2m_tags'):
        op.drop_table('image_m2m_tags')

    # Repeat for 'comments', 'images', 'users', and 'tags'

    # ### end Alembic commands ###

