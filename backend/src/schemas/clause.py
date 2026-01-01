"""Clause schemas for API responses"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class RiskFlagResponse(BaseModel):
    """Risk flag response"""
    flag: str = Field(description="Risk flag type")
    description: str = Field(description="Description of the risk flag")


class ClauseResponse(BaseModel):
    """Clause response schema"""
    id: UUID
    document_id: UUID
    clause_type: str = Field(description="Type of clause (e.g., 'Termination', 'Payment')")
    extracted_text: str = Field(description="Complete text of the clause")
    page_number: int = Field(description="Page number where clause appears")
    section: Optional[str] = Field(description="Section name")
    confidence_score: Optional[float] = Field(description="Confidence score (0.0-1.0)")
    risk_score: float = Field(description="Risk score (0-100)")
    risk_flags: List[str] = Field(default_factory=list, description="List of risk flags")
    risk_reasoning: Optional[str] = Field(description="Explanation of risk factors")
    clause_subtype: Optional[str] = Field(description="Subtype classification")
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class ClauseExtractionRequest(BaseModel):
    """Request to extract clauses from a document"""
    force_re_extract: bool = Field(
        default=False,
        description="Force re-extraction even if clauses already exist"
    )


class ClauseExtractionResponse(BaseModel):
    """Response from clause extraction"""
    document_id: UUID
    clauses_extracted: int = Field(description="Number of clauses extracted")
    clauses: List[ClauseResponse] = Field(description="List of extracted clauses")
    message: str = Field(description="Status message")


class ClauseListResponse(BaseModel):
    """List of clauses response"""
    total: int = Field(description="Total number of clauses")
    clauses: List[ClauseResponse] = Field(description="List of clauses")


class ClauseFilterParams(BaseModel):
    """Filter parameters for clause queries"""
    clause_type: Optional[str] = Field(default=None, description="Filter by clause type")
    min_risk_score: Optional[float] = Field(default=None, description="Minimum risk score")
    max_risk_score: Optional[float] = Field(default=None, description="Maximum risk score")
    has_risk_flags: Optional[bool] = Field(default=None, description="Only clauses with risk flags")
    page_number: Optional[int] = Field(default=None, description="Filter by page number")
