"""Add browser-scoped idea reactions.

Revision ID: 0003_idea_reactions
Revises: 0002_ideas
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_idea_reactions"
down_revision = "0002_ideas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "idea_reactions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), primary_key=True),
        sa.Column("idea_id", sa.Uuid(), sa.ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_key", sa.String(64), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.CheckConstraint("value IN (-1, 1)", name="ck_idea_reactions_value"),
        sa.UniqueConstraint("idea_id", "client_key", name="uq_idea_reactions_idea_client"),
    )
    op.create_index("ix_idea_reactions_idea_id", "idea_reactions", ["idea_id"])


def downgrade() -> None:
    op.drop_index("ix_idea_reactions_idea_id", table_name="idea_reactions")
    op.drop_table("idea_reactions")
