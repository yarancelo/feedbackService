"""Separate suggestions from feedback submissions.

Revision ID: 0006_submission_type
Revises: 0005_idea_comments
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_submission_type"
down_revision = "0005_idea_comments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ideas", sa.Column("submission_type", sa.String(20), nullable=False, server_default="idea"))


def downgrade() -> None:
    op.drop_column("ideas", "submission_type")
