"""fixing db

Revision ID: 05677a03cb73
Revises: 7250eaf9f375
Create Date: 2025-03-12 02:38:40.384024

"""
from typing import Sequence, Union

from scripts.alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "05677a03cb73"
down_revision: Union[str, None] = "7250eaf9f375"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
