"""Updated User Model

Revision ID: 65893052274e
Revises: 028d3bc4b2c4
Create Date: 2024-11-12 10:11:56.551392

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '65893052274e'
down_revision = '028d3bc4b2c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('firstname', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('lastname', sa.String(length=50), nullable=False))
        batch_op.alter_column('control_number',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
        batch_op.drop_column('first_name')
        batch_op.drop_column('last_login')
        batch_op.drop_column('last_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_name', mysql.VARCHAR(length=50), nullable=False))
        batch_op.add_column(sa.Column('last_login', mysql.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('first_name', mysql.VARCHAR(length=50), nullable=False))
        batch_op.alter_column('control_number',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
        batch_op.drop_column('lastname')
        batch_op.drop_column('firstname')

    # ### end Alembic commands ###