"""empty message

Revision ID: 0c7de176cce9
Revises: df9da53df1bb
Create Date: 2024-12-22 23:35:28.952749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c7de176cce9'
down_revision = 'df9da53df1bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('observation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('effectiveDateTime', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('observation', schema=None) as batch_op:
        batch_op.drop_column('effectiveDateTime')
        batch_op.drop_column('category')

    # ### end Alembic commands ###