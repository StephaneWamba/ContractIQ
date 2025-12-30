from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel, field_serializer
import io

from src.core.database import get_db
from src.models.document import Document, DocumentType
from src.services.document_processor import DocumentProcessor


router = APIRouter()


class DocumentResponse(BaseModel):
    id: str
    workspace_id: str
    document_type: str
    status: str
    file_name: str
    file_size: int
    page_count: int | None
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    workspace_id: str = Query(..., description="Workspace ID"),
    document_type: DocumentType = Query(..., description="Document type"),
    file: UploadFile = File(..., description="Document file (PDF or DOCX)"),
    db: Session = Depends(get_db),
):
    """Upload and process a document"""
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    processor = DocumentProcessor(db)
    try:
        document = await processor.process_document(workspace_id, document_type, file)
        # Refresh the document to get updated status
        db.refresh(document)
        return document
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = f"Failed to process document: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR: {error_detail}")  # Log to console
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("/workspace/{workspace_id}", response_model=List[DocumentResponse])
async def list_documents(workspace_id: str, db: Session = Depends(get_db)):
    """List all documents in a workspace"""
    documents = db.query(Document).filter(Document.workspace_id == workspace_id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get a document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/download")
async def download_document(document_id: str, db: Session = Depends(get_db)):
    """Download document file"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    processor = DocumentProcessor(db)
    try:
        file_content = processor.get_document_file(document)
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{document.file_name}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    processor = DocumentProcessor(db)
    try:
        processor.delete_document(document)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

