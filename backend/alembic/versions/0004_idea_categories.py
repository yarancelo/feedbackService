"""Add administrator-managed idea themes.

Revision ID: 0004_idea_categories
Revises: 0003_idea_reactions
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_idea_categories"
down_revision = "0003_idea_reactions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "idea_categories",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    categories = ["Сервис", "Процессы", "Команда", "Клиенты", "Экономия", "Другое"]
    for index, name in enumerate(categories):
        op.execute(sa.text("INSERT INTO idea_categories (name, sort_order, is_active) VALUES (:name, :sort_order, true)").bindparams(name=name, sort_order=index))


def downgrade() -> None:
    op.drop_table("idea_categories")
