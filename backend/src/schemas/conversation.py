"""Conversation schemas for API responses"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID


class CitationResponse(BaseModel):
    """Citation response schema"""
    document_id: str
    document_name: str
    page_number: int
    section_name: str
    text_excerpt: str
    similarity_score: float
    chunk_id: Optional[str] = None
    coordinates: Optional[Dict] = Field(
        default=None,
        description="Bounding box coordinates for highlighting: {x0, y0, x1, y1, page}"
    )


class MessageResponse(BaseModel):
    """Message response schema"""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    citations: Optional[List[CitationResponse]] = None
    message_index: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: UUID
    workspace_id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class AskQuestionRequest(BaseModel):
    """Request to ask a question"""
    question: str = Field(description="User's question")
    document_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional: Filter to specific document IDs"
    )


class AskQuestionResponse(BaseModel):
    """Response from asking a question"""
    answer: str = Field(description="Generated answer")
    citations: List[CitationResponse] = Field(description="Source citations")
    message_id: UUID = Field(description="Message ID")
    conversation_id: UUID = Field(description="Conversation ID")
    retrieved_chunks_count: int = Field(description="Number of chunks retrieved")


class ConversationListResponse(BaseModel):
    """List of conversations"""
    total: int
    conversations: List[ConversationResponse]


class ConversationUpdate(BaseModel):
    """Update conversation request"""
    title: Optional[str] = Field(default=None, description="New conversation title")
