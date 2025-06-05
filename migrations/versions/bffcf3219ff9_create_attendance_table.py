"""create attendance table

Revision ID: bffcf3219ff9
Revises: 1ba1f16e633d
Create Date: 2025-06-02 18:20:07.210888

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision =  'bffcf3219ff9'
down_revision = '1ba1f16e633d'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('athlete_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('status', sa.String(10), nullable=False),
    )

def downgrade():
    op.drop_table('attendance')

