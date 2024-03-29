"""Adding suffix field

Revision ID: ac3ce183cdb5
Revises: cd4835a51fcb
Create Date: 2019-10-12 10:09:39.583194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac3ce183cdb5'
down_revision = 'cd4835a51fcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channel', sa.Column('num_suffix', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('channel', 'num_suffix')
    # ### end Alembic commands ###
