from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import uuid
import enum

from src.core.database import Base


class DocumentType(str, enum.Enum):
    PURCHASE_ORDER = "purchase_order"
    INVOICE = "invoice"
    DELIVERY_NOTE = "delivery_note"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Path in MinIO
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    extracted_data = relationship("ExtractedData", back_populates="document", uselist=False)
    # Note: matching_results relationship removed due to multiple foreign keys
    # Access via: MatchingResult.po_document, MatchingResult.invoice_document, etc.

