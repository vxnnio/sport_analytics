"""add line_user_id column to user table

Revision ID: ca3813ec9694
Revises: 0d2bc0741637
Create Date: 2025-08-12 17:35:10.593597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca3813ec9694'
down_revision = '0d2bc0741637'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('line_user_id', sa.String(length=128), nullable=True))
    op.create_unique_constraint('uq_user_line_user_id', 'user', ['line_user_id'])

def downgrade():
    op.drop_constraint('uq_user_line_user_id', 'user', type_='unique')
    op.drop_column('user', 'line_user_id')