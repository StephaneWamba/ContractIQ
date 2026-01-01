"""Clause model"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from src.core.database import Base


class Clause(Base):
    """Extracted clause model"""

    __tablename__ = "clauses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey(
        "documents.id"), nullable=False)
    # e.g., "Termination", "Liability", "Payment"
    clause_type = Column(String(100), nullable=False)
    extracted_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=False)
    section = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True, default=0.0)  # Risk score 0-100
    risk_flags = Column(JSON, nullable=True)  # List of risk flags
    risk_reasoning = Column(Text, nullable=True)  # Explanation of risk factors
    # Subtype classification
    clause_subtype = Column(String(100), nullable=True)
    # PDF coordinates for highlighting
    coordinates = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="clauses")

    def __repr__(self):
        return f"<Clause(id={self.id}, type={self.clause_type}, page={self.page_number})>"
