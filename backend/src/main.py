"""Main FastAPI application"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from pathlib import Path
import traceback

from src.core.config import settings
from src.core.database import engine, Base
from src.core.logging_config import setup_logging, get_logger
from src.core.exceptions import ContractIQException
from src.schemas.errors import ErrorResponse
from src.api import workspaces, documents, clauses, conversations, auth, exports
import logging

# Set up logging
log_level = getattr(settings, 'log_level', 'INFO')
if not hasattr(logging, log_level.upper()):
    log_level = 'INFO'  # Fallback to INFO if invalid level

setup_logging(
    level=log_level,
    json_format=getattr(settings, 'environment',
                        'development') == "production",
    log_file=Path(getattr(settings, 'log_file', None)) if hasattr(
        settings, 'log_file') and getattr(settings, 'log_file', None) else None
)
logger = get_logger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="ContractIQ API",
    description="Document Intelligence & RAG Platform",
    version="0.1.0"
)

# CORS middleware
logger.info(f"CORS_ORIGINS env value: '{settings.cors_origins}'")
cors_origins_list = [origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()]
if not cors_origins_list:
    cors_origins_list = ["http://localhost:3000"]  # Fallback
    logger.warning("No valid CORS origins found, using fallback")

logger.info(f"CORS origins configured: {cors_origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ContractIQException)
async def contractiq_exception_handler(request: Request, exc: ContractIQException):
    """Handle ContractIQ custom exceptions"""
    logger.error(
        f"ContractIQException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=True,
            error_code=exc.error_code,
            message=exc.user_message,
            details=exc.details,
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "code": error["type"]
        })

    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=True,
            error_code="VALIDATION_ERROR",
            message="Invalid request data. Please check your input.",
            details={"validation_errors": errors},
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    error_id = id(exc)  # Simple error ID for tracking
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
        exc_info=True
    )

    # In production, don't expose internal error details
    if settings.environment == "production":
        message = "An internal error occurred. Please try again later."
        details = {"error_id": str(error_id)}
    else:
        message = f"Internal error: {str(exc)}"
        details = {
            "error_id": str(error_id),
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=True,
            error_code="INTERNAL_ERROR",
            message=message,
            details=details,
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )

# Include routers
app.include_router(
    workspaces.router,
    prefix=f"{settings.api_v1_prefix}/workspaces",
    tags=["workspaces"]
)

app.include_router(
    documents.router,
    prefix=f"{settings.api_v1_prefix}/documents",
    tags=["documents"]
)

app.include_router(
    clauses.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["clauses"]
)

app.include_router(
    conversations.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["conversations"]
)

app.include_router(
    auth.router,
    prefix=f"{settings.api_v1_prefix}/auth",
    tags=["authentication"]
)

app.include_router(
    exports.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["exports"]
)


@app.get("/")
def root():
    """Root endpoint"""
    return {"status": "ok", "message": "ContractIQ API"}


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}
