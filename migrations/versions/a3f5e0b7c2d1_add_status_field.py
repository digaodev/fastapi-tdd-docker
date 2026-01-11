"""add status field

Revision ID: a3f5e0b7c2d1
Revises: 8c13d10608f1
Create Date: 2026-01-11 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f5e0b7c2d1"
down_revision: str | Sequence[str] | None = "8c13d10608f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column with default value 'pending'
    op.add_column(
        "textsummary",
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove status column
    op.drop_column("textsummary", "status")
