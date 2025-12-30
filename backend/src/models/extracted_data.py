from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, unique=True)
    
    # Header fields
    po_number = Column(String)
    invoice_number = Column(String)
    delivery_note_number = Column(String)
    vendor_name = Column(String)
    vendor_address = Column(String)
    date = Column(DateTime)
    total_amount = Column(Numeric(10, 2))
    
    # Financial fields
    currency_code = Column(String)  # ISO currency code (USD, EUR, GBP, etc.)
    subtotal = Column(Numeric(10, 2))  # Amount before tax
    tax_amount = Column(Numeric(10, 2))  # Total tax amount
    tax_rate = Column(Numeric(5, 2))  # Tax rate percentage
    due_date = Column(DateTime)  # Payment due date
    
    # Line items (stored as JSON)
    line_items = Column(JSON)
    
    # Extraction metadata
    confidence_scores = Column(JSON)  # Field-level confidence scores
    extraction_model = Column(String)  # Which model was used
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="extracted_data")


class LineItem:
    """Pydantic-like structure for line items (stored as JSON)"""
    def __init__(
        self,
        item_number: str,
        description: str,
        quantity: float,
        unit_price: float,
        line_total: float,
    ):
        self.item_number = item_number
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.line_total = line_total

