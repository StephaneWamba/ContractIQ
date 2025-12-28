"""Initial migration: Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_temporary', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('document_type', sa.Enum('PURCHASE_ORDER', 'INVOICE', 'DELIVERY_NOTE', name='documenttype'), nullable=False),
        sa.Column('status', sa.Enum('UPLOADED', 'PROCESSING', 'PROCESSED', 'FAILED', name='documentstatus'), nullable=True, server_default='UPLOADED'),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create extracted_data table
    op.create_table(
        'extracted_data',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('po_number', sa.String(), nullable=True),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('delivery_note_number', sa.String(), nullable=True),
        sa.Column('vendor_name', sa.String(), nullable=True),
        sa.Column('vendor_address', sa.String(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('line_items', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('extraction_model', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )

    # Create matching_results table
    op.create_table(
        'matching_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('po_document_id', sa.String(), nullable=True),
        sa.Column('invoice_document_id', sa.String(), nullable=True),
        sa.Column('delivery_note_document_id', sa.String(), nullable=True),
        sa.Column('match_confidence', sa.String(), nullable=True),
        sa.Column('matched_by', sa.String(), nullable=True),
        sa.Column('total_po_amount', sa.String(), nullable=True),
        sa.Column('total_invoice_amount', sa.String(), nullable=True),
        sa.Column('total_delivery_amount', sa.String(), nullable=True),
        sa.Column('total_difference', sa.String(), nullable=True),
        sa.Column('discrepancies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['po_document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['invoice_document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['delivery_note_document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_documents_workspace_id', 'documents', ['workspace_id'])
    op.create_index('ix_documents_document_type', 'documents', ['document_type'])
    op.create_index('ix_matching_results_workspace_id', 'matching_results', ['workspace_id'])


def downgrade() -> None:
    op.drop_index('ix_matching_results_workspace_id', table_name='matching_results')
    op.drop_index('ix_documents_document_type', table_name='documents')
    op.drop_index('ix_documents_workspace_id', table_name='documents')
    op.drop_table('matching_results')
    op.drop_table('extracted_data')
    op.drop_table('documents')
    op.drop_table('workspaces')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS documenttype')

