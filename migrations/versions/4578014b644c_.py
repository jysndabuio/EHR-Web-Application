"""empty message

Revision ID: 4578014b644c
Revises: 3c70af61a04e
Create Date: 2024-11-18 16:52:07.565666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4578014b644c'
down_revision = '3c70af61a04e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('country', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('country')

    # ### end Alembic commands ###