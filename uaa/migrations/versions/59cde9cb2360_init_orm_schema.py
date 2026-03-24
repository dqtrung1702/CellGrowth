"""Baseline ORM schema (no-op)

Revision ID: 59cde9cb2360
Revises:
Create Date: 2026-03-23 20:52:32.811241
"""

from typing import Sequence, Union

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision: str = "59cde9cb2360"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Baseline only: assuming schema already exists. Future revisions will modify from here.
    pass


def downgrade() -> None:
    # Baseline downgrade: no changes.
    pass
