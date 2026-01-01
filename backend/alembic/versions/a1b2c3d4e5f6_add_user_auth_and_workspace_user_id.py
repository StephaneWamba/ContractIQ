"""add_user_auth_and_workspace_user_id

Revision ID: a1b2c3d4e5f6
Revises: ce01b6abad24
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'ce01b6abad24'  # Update this to the latest migration revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add full_name column to users table if it doesn't exist
    try:
        op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    except Exception:
        # Column might already exist, check if we can alter it
        pass
    
    # Update users table: make hashed_password NOT NULL (if it's currently nullable)
    # Check current state first - if already NOT NULL, this will be a no-op
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.VARCHAR(length=255),
                    nullable=False,
                    existing_nullable=True)
    
    # Add user_id column to workspaces table (nullable initially for migration)
    op.add_column('workspaces', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # For existing workspaces without users, assign to first user if exists
    # Otherwise, they will remain NULL (but new workspaces require user_id)
    op.execute("""
        UPDATE workspaces 
        SET user_id = (SELECT id FROM users LIMIT 1)
        WHERE user_id IS NULL AND EXISTS (SELECT 1 FROM users LIMIT 1)
    """)
    
    # Create index on user_id for performance
    op.create_index(op.f('ix_workspaces_user_id'), 'workspaces', ['user_id'], unique=False)
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_workspaces_user_id',
        'workspaces', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Note: user_id remains nullable in database to allow migration
    # Application layer enforces NOT NULL for new workspaces


def downgrade() -> None:
    # Remove foreign key
    op.drop_constraint('fk_workspaces_user_id', 'workspaces', type_='foreignkey')
    
    # Remove index
    op.drop_index(op.f('ix_workspaces_user_id'), table_name='workspaces')
    
    # Remove user_id column
    op.drop_column('workspaces', 'user_id')
    
    # Revert users table changes
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.VARCHAR(length=255),
                    nullable=True)
    
    # Remove full_name if it was added
    try:
        op.drop_column('users', 'full_name')
    except Exception:
        pass

