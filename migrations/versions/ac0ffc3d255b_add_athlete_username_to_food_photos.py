"""add athlete_username to food_photos

Revision ID: ac0ffc3d255b
Revises: ca3813ec9694
Create Date: 2025-08-19 10:25:29.971089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac0ffc3d255b'
down_revision = 'ca3813ec9694'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('food_photos', sa.Column('athlete_username', sa.String(length=80), nullable=False))

def downgrade():
    op.drop_column('food_photos', 'athlete_username')

