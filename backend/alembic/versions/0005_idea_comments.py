"""Add anonymous comments for accepted ideas.

Revision ID: 0005_idea_comments
Revises: 0004_idea_categories
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_idea_comments"
down_revision = "0004_idea_categories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "idea_comments",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), primary_key=True),
        sa.Column("idea_id", sa.Uuid(), sa.ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_key", sa.String(64), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_idea_comments_idea_id", "idea_comments", ["idea_id"])


def downgrade() -> None:
    op.drop_index("ix_idea_comments_idea_id", table_name="idea_comments")
    op.drop_table("idea_comments")
