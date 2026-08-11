"""Add curator-selected golden status.

Revision ID: 0007_gold_status
Revises: 0006_submission_type
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_gold_status"
down_revision = "0006_submission_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ideas", sa.Column("is_gold", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("ideas", "is_gold")
