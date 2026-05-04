"""rename hashed_password to password

Revision ID: e42db616bfcf
Revises: 4a839ec47a03
Create Date: 2026-05-03 10:11:23.904430

"""

from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e42db616bfcf"
down_revision: Union[str, Sequence[str], None] = "4a839ec47a03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("users", "hashed_password", new_column_name="password")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("users", "password", new_column_name="hashed_password")
