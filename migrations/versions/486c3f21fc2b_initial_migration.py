"""Initial Migration

Revision ID: 486c3f21fc2b
Revises: 
Create Date: 2024-09-08 12:13:35.995803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '486c3f21fc2b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_color', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('favorite_color')

    # ### end Alembic commands ###
