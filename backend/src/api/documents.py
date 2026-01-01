"""Document API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Form, Query, status
from fastapi.responses import FileResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4
from pathlib import Path
import shutil

from src.core.database import get_db, SessionLocal
from src.core.config import settings
from src.core.auth import get_current_user
from src.core.exceptions import NotFoundError, ProcessingError, ValidationError
from src.core.logging_config import get_logger
from src.core.cache import cache_service
from src.models.document import Document, DocumentStatus, DocumentType
from src.models.workspace import Workspace
from src.models.user import User
from src.schemas.document import DocumentResponse, DocumentUploadResponse
from src.services.document_processor import DocumentProcessor
from src.services.vector_store import VectorStore

router = APIRouter()
logger = get_logger(__name__)
vector_store = VectorStore()
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
processor = DocumentProcessor()


def process_document_background(document_id: UUID, file_path: str):
    """
    Background task to process document (runs in separate thread).
    Extracts text, structures document, and indexes for RAG.
    """
    db = SessionLocal()
    document = None
    try:
        document = db.query(Document).filter(
            Document.id == document_id).first()
        if not document:
            logger.warning(f"Document {document_id} not found for processing")
            return

        logger.info(
            f"Starting document processing",
            extra={"document_id": str(document_id), "document_name": document.name}
        )

        # Update status to processing
        document.status = DocumentStatus.PROCESSING
        db.commit()

        # Process document based on type
        try:
            if document.file_type == DocumentType.PDF:
                result = processor.process_pdf(file_path)
            elif document.file_type == DocumentType.DOCX:
                result = processor.process_docx(file_path)
            else:
                raise ProcessingError(
                    message=f"Unsupported file type: {document.file_type}",
                    stage="file_type_validation",
                    user_message="This file type is not supported. Please upload a PDF or DOCX file."
                )
        except Exception as e:
            logger.error(
                f"Error processing document {document_id}",
                extra={"document_id": str(document_id), "error": str(e)},
                exc_info=True
            )
            raise ProcessingError(
                message=f"Failed to process document: {str(e)}",
                stage="document_processing",
                user_message="Failed to process document. Please check the file format and try again."
            ) from e

        # Update document with processing results
        document.page_count = result.get("page_count")
        document.status = DocumentStatus.PROCESSED
        db.commit()

        # Invalidate caches after processing
        cache_service.invalidate_workspace(str(document.workspace_id))

        # Index chunks in vector store for RAG
        chunks = result.get("chunks", [])
        if chunks:
            try:
                indexed_count = vector_store.index_document_chunks(
                    workspace_id=str(document.workspace_id),
                    document_id=str(document.id),
                    document_name=document.name,
                    chunks=chunks
                )
                logger.info(
                    f"Successfully indexed {indexed_count} chunks",
                    extra={"document_id": str(document_id), "chunks_indexed": indexed_count}
                )
            except Exception as e:
                logger.error(
                    f"Error indexing chunks for document {document_id}",
                    extra={"document_id": str(document_id), "error": str(e)},
                    exc_info=True
                )
                # Don't fail the whole process if indexing fails
                # Document is still marked as processed

        logger.info(
            f"Document processing completed successfully",
            extra={"document_id": str(document_id), "pages": document.page_count}
        )

    except ProcessingError:
        # Re-raise processing errors
        if document:
            document.status = DocumentStatus.FAILED
            db.commit()
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error processing document {document_id}",
            extra={"document_id": str(document_id)},
            exc_info=True
        )
        if document:
            document.status = DocumentStatus.FAILED
            db.commit()
    finally:
        db.close()


@router.post("/", response_model=DocumentUploadResponse, status_code=201)
@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)  # Alias for frontend compatibility
def upload_document(
    workspace_id: UUID = Form(...),  # Accept from form data
    background_tasks: BackgroundTasks = BackgroundTasks(),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document.

    Validates file, saves to disk, creates database record,
    and starts background processing.
    """
    # Validate workspace exists and belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Validate file type
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    if file_ext not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not allowed. Allowed types: {settings.allowed_file_types}"
        )

    # Determine document type
    if file_ext == "pdf":
        doc_type = DocumentType.PDF
    elif file_ext == "docx":
        doc_type = DocumentType.DOCX
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save file
    file_id = uuid4()
    file_path = UPLOAD_DIR / f"{file_id}.{file_ext}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

        # Create document record
        document = Document(
            id=file_id,
            workspace_id=workspace_id,
            name=Path(file.filename).stem,
            original_filename=file.filename,
            file_path=str(file_path),
            file_type=doc_type,
            status=DocumentStatus.UPLOADED,
            file_size=file_size
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # Invalidate workspace caches
        cache_service.invalidate_workspace(str(workspace_id))
        cache_service.delete(f"workspace:{workspace_id}:documents")

        # Start background processing
        background_tasks.add_task(
            process_document_background, document.id, str(file_path))

        return DocumentUploadResponse(
            document=DocumentResponse.model_validate(document),
            message="Document uploaded successfully. Processing in background."
        )

    except Exception as e:
        logger.error(
            f"Error uploading document",
            extra={"workspace_id": str(workspace_id), "filename": file.filename},
            exc_info=True
        )
        # Clean up file if database operation failed
        if file_path.exists():
            file_path.unlink()
        raise ProcessingError(
            message=f"Failed to upload document: {str(e)}",
            stage="upload",
            user_message="Failed to upload document. Please check the file and try again."
        ) from e


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents in a workspace (only if workspace belongs to user)"""
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Try cache first
    cache_key = f"workspace:{workspace_id}:documents"
    cached = cache_service.get(cache_key)
    if cached is not None:
        # Convert cached dicts back to Pydantic models
        # Use model_validate with from_attributes=False since we're validating from dicts
        return [DocumentResponse.model_validate(d) if isinstance(d, dict) else d for d in cached]
    
    # Query database
    documents = db.query(Document).filter(
        Document.workspace_id == workspace_id).all()
    
    # Convert SQLAlchemy models to Pydantic response models
    result = [DocumentResponse.model_validate(d) for d in documents]
    
    # Cache result as JSON-serializable dicts (enums will be serialized as their values)
    # Use mode='json' to ensure enums are serialized as their values, not string representations
    cache_service.set(cache_key, [d.model_dump(mode='json') for d in result], ttl=60)
    
    return result


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document (only if workspace belongs to user)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == document.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise NotFoundError("document", str(document_id))
    
    # Convert SQLAlchemy model to Pydantic response model
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/file", response_class=FileResponse)
def get_document_file(
    document_id: UUID,
    token: Optional[str] = Query(None, description="Auth token (alternative to Bearer header for PDF viewer)"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    """Serve the document file (only if workspace belongs to user)"""
    from src.core.auth import decode_access_token
    
    # Try to get user from Bearer token first
    current_user = None
    if credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    current_user = db.query(User).filter(User.id == user_id).first()
        except Exception:
            pass
    
    # If no Bearer token, try query param token (for PDF viewer compatibility)
    if current_user is None and token:
        try:
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    current_user = db.query(User).filter(User.id == user_id).first()
        except Exception:
            pass
    
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == document.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type
    media_type = "application/pdf" if document.file_type == DocumentType.PDF else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    # For PDFs, serve inline (not as download) so they display in iframe
    if document.file_type == DocumentType.PDF:
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=document.original_filename,
            headers={"Content-Disposition": f"inline; filename={document.original_filename}"}
        )
    else:
        # For other file types, allow download
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=document.original_filename
        )


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document (only if workspace belongs to user)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == document.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if Path(document.file_path).exists():
        Path(document.file_path).unlink()

    # Delete from vector store
    vector_store.delete_document(
        workspace_id=str(document.workspace_id),
        document_id=str(document.id)
    )

    # Invalidate caches
    cache_service.invalidate_document(str(document.id), str(document.workspace_id))

    # Delete from database (cascade will delete clauses)
    db.delete(document)
    db.commit()
    return None
