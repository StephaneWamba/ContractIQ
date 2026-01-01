"""
Error response schemas for API.

Provides consistent error response format.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ErrorDetail(BaseModel):
    """Error detail information"""
    field: Optional[str] = Field(None, description="Field name if validation error")
    message: str = Field(description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = Field(True, description="Indicates this is an error response")
    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="User-friendly error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(description="Error timestamp (ISO format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "error_code": "NOT_FOUND",
                "message": "The requested resource was not found.",
                "details": {"resource_type": "document", "resource_id": "123"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

