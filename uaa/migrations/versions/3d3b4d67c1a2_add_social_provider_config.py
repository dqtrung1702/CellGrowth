"""Add social_providers table for storing OAuth client config"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3d3b4d67c1a2"
down_revision: Union[str, None] = "59cde9cb2360"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "social_providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=32), nullable=False, unique=True),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("client_secret_enc", sa.String(), nullable=False),
        sa.Column("redirect_uri", sa.String(), nullable=False),
        sa.Column("scopes", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        schema="uaa",
    )


def downgrade() -> None:
    op.drop_table("social_providers", schema="uaa")
