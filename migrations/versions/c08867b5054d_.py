"""empty message

Revision ID: c08867b5054d
Revises: 9a90c2d39932
Create Date: 2024-12-04 18:59:33.580249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c08867b5054d'
down_revision = '9a90c2d39932'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medication',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('medication_statement_id', sa.Integer(), nullable=False),
    sa.Column('medication_name', sa.String(length=100), nullable=False),
    sa.Column('dosage', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['medication_statement_id'], ['medication_statement.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('medication')
    # ### end Alembic commands ###
