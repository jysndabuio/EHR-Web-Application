"""empty message

Revision ID: 8781cd21f400
Revises: 4578014b644c
Create Date: 2024-11-19 08:44:21.087060

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8781cd21f400'
down_revision = '4578014b644c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_education',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('med_deg', sa.String(length=50), nullable=True),
    sa.Column('med_deg_spec', sa.String(length=50), nullable=True),
    sa.Column('board_cert', sa.String(length=50), nullable=True),
    sa.Column('license_num', sa.String(length=50), nullable=False),
    sa.Column('license_issuer', sa.String(length=50), nullable=True),
    sa.Column('license_expiration', sa.String(length=50), nullable=True),
    sa.Column('years_of_experience', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('med_deg')
        batch_op.drop_column('years_of_experience')
        batch_op.drop_column('board_cert')
        batch_op.drop_column('med_deg_spec')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('med_deg_spec', mysql.VARCHAR(length=50), nullable=True))
        batch_op.add_column(sa.Column('board_cert', mysql.VARCHAR(length=50), nullable=True))
        batch_op.add_column(sa.Column('years_of_experience', mysql.VARCHAR(length=50), nullable=True))
        batch_op.add_column(sa.Column('med_deg', mysql.VARCHAR(length=50), nullable=True))

    op.drop_table('user_education')
    # ### end Alembic commands ###