"""Document model"""
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from src.core.database import Base


class DocumentStatus(enum.Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class DocumentType(enum.Enum):
    """Document type"""
    PDF = "pdf"
    DOCX = "docx"


class Document(Base):
    """Document model"""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey(
        "workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus),
                    default=DocumentStatus.UPLOADED, nullable=False)
    page_count = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    clauses = relationship(
        "Clause", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, name={self.name}, status={self.status.value})>"
