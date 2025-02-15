"""empty message

Revision ID: e63ef80b8f5c
Revises: a88f745f89d4
Create Date: 2024-12-24 18:52:18.524347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e63ef80b8f5c'
down_revision = 'a88f745f89d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('has_submitted_survey', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('has_submitted_survey')

    # ### end Alembic commands ###
