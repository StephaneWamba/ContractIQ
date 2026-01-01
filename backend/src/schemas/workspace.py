"""Workspace schemas"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class WorkspaceCreate(BaseModel):
    """Schema for creating a workspace"""
    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    description: Optional[str] = Field(None, max_length=1000, description="Workspace description")
    is_temporary: bool = Field(default=False, description="Whether workspace is temporary")


class WorkspaceResponse(BaseModel):
    """Schema for workspace response"""
    id: UUID
    name: str
    description: Optional[str]
    is_temporary: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

