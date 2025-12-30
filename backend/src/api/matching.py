from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, field_serializer
from datetime import datetime
import json

from src.core.database import get_db
from src.models.workspace import Workspace
from src.models.document import Document, DocumentStatus
from src.models.matching import MatchingResult
from src.services.matching import MatchingService

router = APIRouter()


class MatchingResultResponse(BaseModel):
    id: str
    workspace_id: str
    po_document_id: str | None
    invoice_document_id: str | None
    delivery_note_document_id: str | None
    match_confidence: dict
    matched_by: str
    total_po_amount: str
    total_invoice_amount: str
    total_delivery_amount: str | None
    total_difference: str
    discrepancies: List[dict]
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle match_confidence JSON string"""
        data = {
            'id': obj.id,
            'workspace_id': obj.workspace_id,
            'po_document_id': obj.po_document_id,
            'invoice_document_id': obj.invoice_document_id,
            'delivery_note_document_id': obj.delivery_note_document_id,
            'matched_by': obj.matched_by,
            'total_po_amount': obj.total_po_amount,
            'total_invoice_amount': obj.total_invoice_amount,
            'total_delivery_amount': obj.total_delivery_amount,
            'total_difference': obj.total_difference,
            'discrepancies': obj.discrepancies or [],
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }
        # Parse match_confidence JSON string
        if obj.match_confidence:
            if isinstance(obj.match_confidence, str):
                try:
                    data['match_confidence'] = json.loads(obj.match_confidence)
                except (json.JSONDecodeError, TypeError):
                    data['match_confidence'] = {}
            else:
                data['match_confidence'] = obj.match_confidence
        else:
            data['match_confidence'] = {}
        return cls(**data)


@router.post("/workspace/{workspace_id}/match", response_model=List[MatchingResultResponse])
async def match_documents(workspace_id: str, db: Session = Depends(get_db)):
    """Match documents in a workspace"""
    # Verify workspace exists
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check document statuses for debugging
    all_docs = db.query(Document).filter(Document.workspace_id == workspace_id).all()
    processed_docs = [d for d in all_docs if d.status == DocumentStatus.PROCESSED]
    processing_docs = [d for d in all_docs if d.status == DocumentStatus.PROCESSING]
    failed_docs = [d for d in all_docs if d.status == DocumentStatus.FAILED]
    
    if len(processed_docs) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"No processed documents found. Found {len(all_docs)} total documents: {len(processing_docs)} processing, {len(failed_docs)} failed. Please wait for documents to finish processing or check for errors."
        )
    
    if len(processed_docs) < 2:
        doc_types = [d.document_type.value for d in processed_docs]
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 2 processed documents to match. Found {len(processed_docs)} processed document(s): {', '.join(doc_types)}. Please upload at least a PO and Invoice."
        )

    # Run matching
    matching_service = MatchingService(db)
    results = matching_service.match_documents_in_workspace(workspace_id)
    
    if len(results) == 0:
        # Provide helpful error message
        po_count = len([d for d in processed_docs if d.document_type.value == "purchase_order"])
        inv_count = len([d for d in processed_docs if d.document_type.value == "invoice"])
        dn_count = len([d for d in processed_docs if d.document_type.value == "delivery_note"])
        
        detail = f"No matches found. Processed documents: {po_count} PO(s), {inv_count} Invoice(s), {dn_count} Delivery Note(s). "
        detail += "Matching requires: (1) At least one PO and one Invoice, (2) Matching PO numbers or vendor names, (3) Extracted data with PO numbers or vendor names."
        raise HTTPException(status_code=404, detail=detail)

    # Convert to response models
    return [MatchingResultResponse.from_orm(r) for r in results]


@router.get("/workspace/{workspace_id}/results", response_model=List[MatchingResultResponse])
async def get_matching_results(workspace_id: str, db: Session = Depends(get_db)):
    """Get matching results for a workspace"""
    # Verify workspace exists
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Get all matching results
    results = db.query(MatchingResult).filter(
        MatchingResult.workspace_id == workspace_id
    ).all()

    # Convert to response models
    return [MatchingResultResponse.from_orm(r) for r in results]


@router.get("/{result_id}", response_model=MatchingResultResponse)
async def get_matching_result(result_id: str, db: Session = Depends(get_db)):
    """Get a specific matching result"""
    result = db.query(MatchingResult).filter(MatchingResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Matching result not found")
    return MatchingResultResponse.from_orm(result)
