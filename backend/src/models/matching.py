from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import uuid
import enum

from src.core.database import Base


class DiscrepancyType(str, enum.Enum):
    QUANTITY_MISMATCH = "quantity_mismatch"
    PRICE_CHANGE = "price_change"
    MISSING_ITEM = "missing_item"
    EXTRA_ITEM = "extra_item"
    DESCRIPTION_MISMATCH = "description_mismatch"


class DiscrepancySeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MatchingResult(Base):
    __tablename__ = "matching_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    
    # Matched documents
    po_document_id = Column(String, ForeignKey("documents.id"))
    invoice_document_id = Column(String, ForeignKey("documents.id"))
    delivery_note_document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    
    # Matching metadata
    match_confidence = Column(String)  # JSON with confidence scores
    matched_by = Column(String)  # "po_number" or "vendor_name"
    
    # Comparison results
    total_po_amount = Column(String)  # Numeric as string for JSON compatibility
    total_invoice_amount = Column(String)
    total_delivery_amount = Column(String, nullable=True)
    total_difference = Column(String)
    
    # Discrepancies (stored as JSON array)
    discrepancies = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace")
    po_document = relationship("Document", foreign_keys=[po_document_id])
    invoice_document = relationship("Document", foreign_keys=[invoice_document_id])
    delivery_note_document = relationship("Document", foreign_keys=[delivery_note_document_id])


class Discrepancy:
    """Pydantic-like structure for discrepancies (stored as JSON)"""
    def __init__(
        self,
        type: DiscrepancyType,
        severity: DiscrepancySeverity,
        item_number: str,
        description: str,
        po_value: dict,
        invoice_value: dict,
        delivery_value: dict = None,
        message: str = None,
    ):
        self.type = type
        self.severity = severity
        self.item_number = item_number
        self.description = description
        self.po_value = po_value
        self.invoice_value = invoice_value
        self.delivery_value = delivery_value
        self.message = message

