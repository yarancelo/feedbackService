from alembic import op
import sqlalchemy as sa
revision='0008_manual_authors'; down_revision='0007_gold_status'; branch_labels=None; depends_on=None
def upgrade():
    op.create_table('manual_authors', sa.Column('id', sa.Uuid(), primary_key=True, server_default=sa.text('uuidv7()')), sa.Column('full_name', sa.String(255), nullable=False, unique=True), sa.Column('department', sa.String(255)), sa.Column('company', sa.String(255)), sa.Column('position', sa.String(255)), sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')))
def downgrade(): op.drop_table('manual_authors')
