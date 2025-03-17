"""new migration

Revision ID: 7d379beec5f9
Revises: 
Create Date: 2025-03-12 19:52:57.734114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d379beec5f9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coins',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('github', sa.String(), nullable=True),
    sa.Column('x', sa.String(), nullable=True),
    sa.Column('reddit', sa.String(), nullable=True),
    sa.Column('telegram', sa.String(), nullable=True),
    sa.Column('website', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coins_id'), 'coins', ['id'], unique=False)
    op.create_index(op.f('ix_coins_symbol'), 'coins', ['symbol'], unique=True)
    op.create_table('scoring_weights',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('liquidity_score', sa.Float(), nullable=False),
    sa.Column('developer_score', sa.Float(), nullable=False),
    sa.Column('community_score', sa.Float(), nullable=False),
    sa.Column('market_score', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scoring_weights_id'), 'scoring_weights', ['id'], unique=False)
    op.create_table('user_activities',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('resource_type', sa.String(), nullable=False),
    sa.Column('resource_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_activities_id'), 'user_activities', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('role', sa.Enum('ANALYST', 'MANAGER', name='userrole'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('metrics',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('coin_id', sa.UUID(), nullable=False),
    sa.Column('market_cap', sa.JSON(), nullable=False),
    sa.Column('volume_24h', sa.JSON(), nullable=False),
    sa.Column('liquidity', sa.JSON(), nullable=False),
    sa.Column('github_activity', sa.JSON(), nullable=True),
    sa.Column('twitter_sentiment', sa.JSON(), nullable=True),
    sa.Column('reddit_sentiment', sa.JSON(), nullable=True),
    sa.Column('fetched_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['coin_id'], ['coins.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metrics_coin_id'), 'metrics', ['coin_id'], unique=False)
    op.create_index(op.f('ix_metrics_id'), 'metrics', ['id'], unique=False)
    op.create_table('scores',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('coin_id', sa.UUID(), nullable=False),
    sa.Column('scoring_weight_id', sa.UUID(), nullable=False),
    sa.Column('liquidity_score', sa.Float(), nullable=False),
    sa.Column('developer_score', sa.Float(), nullable=False),
    sa.Column('community_score', sa.Float(), nullable=False),
    sa.Column('market_score', sa.Float(), nullable=False),
    sa.Column('final_score', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['coin_id'], ['coins.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['scoring_weight_id'], ['scoring_weights.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scores_id'), 'scores', ['id'], unique=False)
    op.create_table('suggestions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('coin_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('note', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='suggestionstatus'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['coin_id'], ['coins.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suggestions_id'), 'suggestions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_suggestions_id'), table_name='suggestions')
    op.drop_table('suggestions')
    op.drop_index(op.f('ix_scores_id'), table_name='scores')
    op.drop_table('scores')
    op.drop_index(op.f('ix_metrics_id'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_coin_id'), table_name='metrics')
    op.drop_table('metrics')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_user_activities_id'), table_name='user_activities')
    op.drop_table('user_activities')
    op.drop_index(op.f('ix_scoring_weights_id'), table_name='scoring_weights')
    op.drop_table('scoring_weights')
    op.drop_index(op.f('ix_coins_symbol'), table_name='coins')
    op.drop_index(op.f('ix_coins_id'), table_name='coins')
    op.drop_table('coins')
    # ### end Alembic commands ###
