"""add order status

Revision ID: b0cd0a89683a
Revises: 9e5121379c70
Create Date: 2026-05-12 10:27:54.907609

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b0cd0a89683a"
down_revision: Union[str, Sequence[str], None] = "9e5121379c70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    orderstatus_enum = sa.Enum(
        "pending", "paid", "shipped", "delivered", name="orderstatus", create_type=True
    )
    orderstatus_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "orders",
        sa.Column("status", orderstatus_enum, server_default="pending", nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "status")
