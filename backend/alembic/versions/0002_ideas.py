"""Migrate legacy feedback into moderated ideas without losing submissions.

Revision ID: 0002_ideas
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_ideas"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("feedbacks", "ideas")
    op.add_column("ideas", sa.Column("category", sa.String(100), nullable=True))
    op.add_column("ideas", sa.Column("visibility", sa.String(20), nullable=False, server_default="anonymous"))
    op.add_column("ideas", sa.Column("status", sa.String(20), nullable=False, server_default="new"))
    op.add_column("ideas", sa.Column("author_bitrix_id", sa.String(100), nullable=True))
    op.add_column("ideas", sa.Column("author_name", sa.String(255), nullable=True))
    op.add_column("ideas", sa.Column("author_company", sa.String(255), nullable=True))
    op.add_column("ideas", sa.Column("author_department", sa.String(255), nullable=True))
    op.add_column("ideas", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("ideas", sa.Column("review_note", sa.Text(), nullable=True))
    op.execute("UPDATE ideas SET status = 'accepted'")
    op.drop_index("ix_feedbacks_created_at", table_name="ideas")
    op.create_index("ix_ideas_created_at", "ideas", ["created_at"])
    op.create_index("ix_ideas_status_created_at", "ideas", ["status", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ideas_status_created_at", table_name="ideas")
    op.drop_index("ix_ideas_created_at", table_name="ideas")
    for column in ("review_note", "reviewed_at", "author_department", "author_company", "author_name", "author_bitrix_id", "status", "visibility", "category"):
        op.drop_column("ideas", column)
    op.rename_table("ideas", "feedbacks")
    op.create_index("ix_feedbacks_created_at", "feedbacks", ["created_at"])
