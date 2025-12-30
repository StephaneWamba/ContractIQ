"""add currency and tax fields

Revision ID: af5c77765af1
Revises: 001_initial
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af5c77765af1'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add currency and tax fields to extracted_data table
    op.add_column('extracted_data', sa.Column('currency_code', sa.String(), nullable=True))
    op.add_column('extracted_data', sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('extracted_data', sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('extracted_data', sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('extracted_data', sa.Column('due_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove currency and tax fields
    op.drop_column('extracted_data', 'due_date')
    op.drop_column('extracted_data', 'tax_rate')
    op.drop_column('extracted_data', 'tax_amount')
    op.drop_column('extracted_data', 'subtotal')
    op.drop_column('extracted_data', 'currency_code')
