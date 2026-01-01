"""
Custom exceptions for ContractIQ API.

Provides structured error handling with user-friendly messages.
"""
from typing import Optional, Dict, Any


class ContractIQException(Exception):
    """Base exception for ContractIQ"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        """
        Initialize exception.
        
        Args:
            message: Internal error message (for logging)
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
            user_message: User-friendly error message (if None, uses message)
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.user_message = user_message or message


class NotFoundError(ContractIQException):
    """Resource not found"""
    
    def __init__(self, resource_type: str, resource_id: str, user_message: Optional[str] = None):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
            user_message=user_message or f"The requested {resource_type.lower()} was not found."
        )


class UnauthorizedError(ContractIQException):
    """Authentication/authorization error"""
    
    def __init__(self, message: str = "Authentication required", user_message: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
            user_message=user_message or "Please log in to access this resource."
        )


class ForbiddenError(ContractIQException):
    """Access forbidden"""
    
    def __init__(self, message: str = "Access forbidden", user_message: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            user_message=user_message or "You don't have permission to access this resource."
        )


class ValidationError(ContractIQException):
    """Validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None, user_message: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
            user_message=user_message or message
        )


class ExternalServiceError(ContractIQException):
    """External service error (OpenAI, etc.)"""
    
    def __init__(
        self,
        service: str,
        message: str,
        retryable: bool = True,
        user_message: Optional[str] = None
    ):
        super().__init__(
            message=f"{service} error: {message}",
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "retryable": retryable},
            user_message=user_message or f"Service temporarily unavailable. Please try again in a moment."
        )
        self.retryable = retryable


class ProcessingError(ContractIQException):
    """Document/clause processing error"""
    
    def __init__(self, message: str, stage: Optional[str] = None, user_message: Optional[str] = None):
        details = {"stage": stage} if stage else {}
        super().__init__(
            message=message,
            status_code=500,
            error_code="PROCESSING_ERROR",
            details=details,
            user_message=user_message or "An error occurred while processing your request. Please try again."
        )


class RateLimitError(ContractIQException):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            user_message="Too many requests. Please wait a moment before trying again."
        )

