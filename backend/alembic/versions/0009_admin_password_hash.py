"""remove default admin and add password hash

Revision ID: 0009_admin_password_hash
Revises: 0008_manual_authors
"""
from alembic import op
import sqlalchemy as sa

revision = '0009_admin_password_hash'
down_revision = '0008_manual_authors'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))
    op.alter_column('users', 'password', existing_type=sa.String(255), nullable=True)
    op.execute("DELETE FROM users WHERE login = 'admin' AND password = 'password'")

def downgrade():
    op.alter_column('users', 'password', existing_type=sa.String(255), nullable=False)
    op.drop_column('users', 'password_hash')
