"""Initial tables for users and birth data

Revision ID: 001
Revises: 
Create Date: 2025-11-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('telegram_id', sa.BigInteger(), nullable=False, comment='Telegram user ID (unique identifier)'),
        sa.Column('username', sa.String(length=255), nullable=True, comment='Telegram username (optional, for convenience)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='Account creation timestamp'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Last update timestamp'),
        sa.PrimaryKeyConstraint('telegram_id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)

    # Create birth_data table
    op.create_table(
        'birth_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='Foreign key to users table'),
        sa.Column('chart_id', sa.String(length=255), nullable=True, comment='Chart ID from Nocturna API'),
        sa.Column('birth_date', sa.String(length=10), nullable=False, comment='Birth date in YYYY-MM-DD format'),
        sa.Column('birth_time', sa.String(length=8), nullable=False, comment='Birth time in HH:MM:SS format'),
        sa.Column('timezone', sa.String(length=50), nullable=False, comment='Timezone name (e.g., Europe/Moscow)'),
        sa.Column('location_name', sa.String(length=255), nullable=True, comment='Human-readable location name (e.g., Москва, Россия)'),
        sa.Column('latitude', sa.Float(), nullable=False, comment='Geographic latitude'),
        sa.Column('longitude', sa.Float(), nullable=False, comment='Geographic longitude'),
        sa.Column('natal_chart_cache', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Cached natal chart calculation data'),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='User preferences (aspect orbs, display settings, etc.)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='Birth data creation timestamp'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_birth_data_user_id'), 'birth_data', ['user_id'], unique=True)
    op.create_index(op.f('ix_birth_data_chart_id'), 'birth_data', ['chart_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_birth_data_user_id'), table_name='birth_data')
    op.drop_table('birth_data')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_table('users')

