"""empty message

Revision ID: 4743cf65fa01
Revises: a58f88fd68f1
Create Date: 2024-01-18 03:27:49.836469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4743cf65fa01'
down_revision = 'a58f88fd68f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('language', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_column('language')

    # ### end Alembic commands ###
