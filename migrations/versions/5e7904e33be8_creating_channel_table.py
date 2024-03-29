"""creating channel table

Revision ID: 5e7904e33be8
Revises: ad39e8c33891
Create Date: 2019-10-09 18:36:09.508580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e7904e33be8'
down_revision = 'ad39e8c33891'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channels',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('cat_id', sa.BigInteger(), nullable=False),
    sa.Column('chan_type', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['cat_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('channels')
    # ### end Alembic commands ###
