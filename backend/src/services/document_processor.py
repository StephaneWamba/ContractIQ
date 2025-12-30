from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import Optional
import uuid
from datetime import datetime

from src.models.document import Document, DocumentType, DocumentStatus
from src.models.extracted_data import ExtractedData
from src.services.storage import storage_service
from src.services.form_recognizer import form_recognizer_service
from src.services.pdf_utils import get_pdf_page_count, validate_pdf
from src.core.config import settings


class DocumentProcessor:
    """Service for processing uploaded documents"""

    def __init__(self, db: Session):
        self.db = db

    async def process_document(
        self,
        workspace_id: str,
        document_type: DocumentType,
        file: UploadFile,
    ) -> Document:
        """Process uploaded document: validate, store, extract data"""

        # Read file content
        file_content = await file.read()

        # Validate file size
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / 1024 / 1024}MB")

        # Validate PDF
        if file.filename.endswith(".pdf"):
            is_valid, error_msg = validate_pdf(file_content, settings.MAX_PAGES)
            if not is_valid:
                raise ValueError(error_msg)
            page_count = get_pdf_page_count(file_content)
        else:
            page_count = None

        # Generate unique file path
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "pdf"
        file_path = f"{workspace_id}/{file_id}.{file_extension}"

        # Upload to storage
        content_type = file.content_type or "application/pdf"
        storage_service.upload_file(file_content, file_path, content_type)

        # Create document record
        document = Document(
            workspace_id=workspace_id,
            document_type=document_type,
            status=DocumentStatus.UPLOADED,
            file_name=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            page_count=page_count,
        )
        self.db.add(document)
        self.db.flush()  # Get document ID

        # Update status to processing
        document.status = DocumentStatus.PROCESSING
        self.db.commit()

        try:
            # Extract data using Azure Form Recognizer
            extracted_data_dict = form_recognizer_service.extract_document(document_type, file_content)

            # Create extracted data record
            extracted_data = ExtractedData(
                document_id=document.id,
                po_number=extracted_data_dict.get("po_number"),
                invoice_number=extracted_data_dict.get("invoice_number"),
                delivery_note_number=extracted_data_dict.get("delivery_note_number"),
                vendor_name=extracted_data_dict.get("vendor_name"),
                vendor_address=extracted_data_dict.get("vendor_address"),
                date=extracted_data_dict.get("date"),
                total_amount=extracted_data_dict.get("total_amount"),
                currency_code=extracted_data_dict.get("currency_code"),
                subtotal=extracted_data_dict.get("subtotal"),
                tax_amount=extracted_data_dict.get("tax_amount"),
                tax_rate=extracted_data_dict.get("tax_rate"),
                due_date=extracted_data_dict.get("due_date"),
                line_items=extracted_data_dict.get("line_items", []),
                confidence_scores=extracted_data_dict.get("confidence_scores", {}),
                extraction_model="azure-form-recognizer",
            )
            self.db.add(extracted_data)

            # Update document status
            document.status = DocumentStatus.PROCESSED
            self.db.commit()

        except Exception as e:
            # Update status to failed
            document.status = DocumentStatus.FAILED
            self.db.commit()
            raise Exception(f"Failed to extract data from document: {str(e)}")

        return document

    def get_document_file(self, document: Document) -> bytes:
        """Retrieve document file from storage"""
        return storage_service.get_file(document.file_path)

    def delete_document(self, document: Document):
        """Delete document and its file from storage"""
        # Delete from storage
        storage_service.delete_file(document.file_path)
        # Delete from database (cascade will handle related records)
        self.db.delete(document)
        self.db.commit()

