"""Authentication schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="Password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")


class Token(BaseModel):
    """JWT token response"""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile with token"""
    user: UserResponse
    token: Token

