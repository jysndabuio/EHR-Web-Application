"""empty message

Revision ID: 9bb0ed75b190
Revises: 7e7a0ab96b84
Create Date: 2024-12-04 22:44:33.280578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bb0ed75b190'
down_revision = '7e7a0ab96b84'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('observation', schema=None) as batch_op:
        batch_op.drop_column('effectiveDateTime')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('observation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('effectiveDateTime', sa.DATE(), nullable=True))

    # ### end Alembic commands ###