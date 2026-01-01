"""Document schemas"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

from src.models.document import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: UUID
    workspace_id: UUID
    name: str
    original_filename: str
    file_path: str
    file_type: DocumentType
    status: DocumentStatus
    page_count: Optional[int]
    file_size: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    document: DocumentResponse
    message: str = Field(default="Document uploaded successfully")

