"""Add confirmed local authors.

Revision ID: 0004_manual_authors
Revises: 0003_idea_reactions
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_manual_authors"
down_revision = "0003_idea_reactions"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("manual_authors", sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), primary_key=True), sa.Column("full_name", sa.String(255), nullable=False, unique=True), sa.Column("position", sa.String(255)), sa.Column("company", sa.String(255)), sa.Column("department", sa.String(255)))

def downgrade() -> None:
    op.drop_table("manual_authors")
