"""empty message

Revision ID: 7e7a0ab96b84
Revises: c08867b5054d
Create Date: 2024-12-04 19:10:32.536731

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7e7a0ab96b84'
down_revision = 'c08867b5054d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('medication')
    with op.batch_alter_table('medication_statement', schema=None) as batch_op:
        batch_op.add_column(sa.Column('medication', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('dosage', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medication_statement', schema=None) as batch_op:
        batch_op.drop_column('dosage')
        batch_op.drop_column('medication')

    op.create_table('medication',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('medication_statement_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('medication_name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('dosage', mysql.VARCHAR(length=50), nullable=True),
    sa.ForeignKeyConstraint(['medication_statement_id'], ['medication_statement.id'], name='medication_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
