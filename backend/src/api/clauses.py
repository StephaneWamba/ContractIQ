"""Clause extraction and management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID

from src.core.database import get_db
from src.core.auth import get_current_user
from src.core.cache import cache_service
from src.core.logging_config import get_logger
from src.models.document import Document, DocumentStatus
from src.models.clause import Clause
from src.models.workspace import Workspace
from src.models.user import User
from src.schemas.clause import (
    ClauseResponse,
    ClauseExtractionRequest,
    ClauseExtractionResponse,
    ClauseListResponse
)
from src.services.clause_extractor import ClauseExtractor
from src.services.vector_store import VectorStore
from src.services.clause_deduplicator import ClauseDeduplicator

router = APIRouter()
logger = get_logger(__name__)
clause_extractor = ClauseExtractor()
vector_store = VectorStore()
clause_deduplicator = ClauseDeduplicator()


@router.post(
    "/documents/{document_id}/extract-clauses",
    response_model=ClauseExtractionResponse,
    status_code=200
)
def extract_clauses(
    document_id: UUID,
    request: ClauseExtractionRequest = ClauseExtractionRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract clauses from a processed document.

    This endpoint:
    1. Retrieves document chunks from vector store
    2. Uses LLM to extract clauses with risk analysis
    3. Stores extracted clauses in database
    4. Returns extracted clauses with risk flags
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        logger.warning(f"Document {document_id} not found for clause extraction")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.info(f"Starting clause extraction for document {document_id} ({document.name})")

    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == document.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if document is processed
    if document.status != DocumentStatus.PROCESSED:
        raise HTTPException(
            status_code=400,
            detail=f"Document must be processed before clause extraction. Current status: {document.status.value}"
        )

    # Check if clauses already exist
    existing_clauses = db.query(Clause).filter(
        Clause.document_id == document_id).count()
    if existing_clauses > 0 and not request.force_re_extract:
        # Return existing clauses
        clauses = db.query(Clause).filter(
            Clause.document_id == document_id).all()
        return ClauseExtractionResponse(
            document_id=document_id,
            clauses_extracted=len(clauses),
            clauses=[ClauseResponse.from_orm(c) for c in clauses],
            message="Using existing clauses. Set force_re_extract=true to re-extract."
        )

    # Delete existing clauses if re-extracting
    if existing_clauses > 0 and request.force_re_extract:
        db.query(Clause).filter(Clause.document_id == document_id).delete()
        db.commit()

    # Get chunks from vector store
    collection = vector_store.get_or_create_collection(
        str(document.workspace_id))
    all_data = collection.get(
        where={"document_id": str(document_id)},
        include=["documents", "metadatas"]
    )

    if not all_data.get("documents") or len(all_data["documents"]) == 0:
        raise HTTPException(
            status_code=404,
            detail="No chunks found for this document. Document may not be fully processed."
        )

    # Prepare chunks for extraction
    chunks = []
    for i, doc_text in enumerate(all_data["documents"]):
        metadata = all_data["metadatas"][i] if all_data.get(
            "metadatas") else {}
        chunks.append({
            "text": doc_text,
            "page_number": metadata.get("page_number", 0),
            "section_name": metadata.get("section_name", "Unknown"),
            "chunk_id": all_data["ids"][i] if all_data.get("ids") else f"chunk_{i}"
        })

    # Extract clauses
    extracted_clauses = clause_extractor.extract_clauses_from_document(
        document_id=str(document_id),
        chunks=chunks
    )

    # Deduplicate using LLM-based intelligent comparison
    extracted_clauses = clause_deduplicator.deduplicate_clauses(
        extracted_clauses)

    # Validate and ensure risk_reasoning exists for all clauses
    validated_clauses = []
    for clause in extracted_clauses:
        # Skip invalid clauses
        if not clause.extracted_text or len(clause.extracted_text.strip()) < 10:
            continue

        # Ensure risk_score is within bounds
        if clause.risk_score < 0:
            clause.risk_score = 0.0
        elif clause.risk_score > 100:
            clause.risk_score = 100.0

        # Ensure risk_reasoning exists (LLM should provide, but fallback if missing)
        if not clause.risk_reasoning or not clause.risk_reasoning.strip():
            # Generate fallback reasoning based on score
            if clause.risk_score >= 75:
                clause.risk_reasoning = f"Critical risk (score: {clause.risk_score}) - This clause requires immediate attention and negotiation."
            elif clause.risk_score >= 50:
                clause.risk_reasoning = f"High risk (score: {clause.risk_score}) - Significant concerns identified. Review and negotiation recommended."
            elif clause.risk_score >= 25:
                clause.risk_reasoning = f"Medium risk (score: {clause.risk_score}) - Some concerns identified. Review recommended."
            else:
                clause.risk_reasoning = f"Low risk (score: {clause.risk_score}) - Standard or acceptable clause terms."

        validated_clauses.append(clause)

    extracted_clauses = validated_clauses

    # Store clauses in database
    db_clauses = []
    for clause in extracted_clauses:
        db_clause = Clause(
            document_id=document_id,
            clause_type=clause.clause_type.value,
            extracted_text=clause.extracted_text,
            page_number=clause.page_number,
            section=clause.section_name,
            confidence_score=clause.confidence_score,
            risk_score=clause.risk_score,
            risk_flags=clause.risk_flags,  # Already a list of strings
            risk_reasoning=clause.risk_reasoning,
            clause_subtype=clause.clause_subtype,
            coordinates=None  # TODO: Extract coordinates from PDF
        )
        db.add(db_clause)
        db_clauses.append(db_clause)

    # Re-validate document exists before commit (prevent race conditions)
    document_still_exists = db.query(Document).filter(Document.id == document_id).first()
    if not document_still_exists:
        logger.error(f"Document {document_id} disappeared during clause extraction - possible race condition")
        db.rollback()
        raise HTTPException(
            status_code=410,  # Gone
            detail="Document was deleted during clause extraction. Please re-upload the document."
        )

    logger.info(f"Committing {len(db_clauses)} clauses for document {document_id}")
    db.commit()

    # Refresh to get IDs
    for clause in db_clauses:
        db.refresh(clause)

    # Invalidate document and workspace caches
    cache_service.invalidate_document(
        str(document_id), str(document.workspace_id))
    cache_service.delete(f"document:{document_id}:clauses")

    # Build response - convert risk_flags from list to list of strings
    clause_responses = []
    for c in db_clauses:
        # Convert risk_flags JSON to list of strings
        risk_flags_list = c.risk_flags if c.risk_flags else []
        if not isinstance(risk_flags_list, list):
            risk_flags_list = []

        clause_responses.append(ClauseResponse(
            id=c.id,
            document_id=c.document_id,
            clause_type=c.clause_type,
            extracted_text=c.extracted_text,
            page_number=c.page_number,
            section=c.section,
            confidence_score=c.confidence_score,
            risk_score=c.risk_score or 0.0,
            risk_flags=risk_flags_list,
            risk_reasoning=c.risk_reasoning,
            clause_subtype=c.clause_subtype,
            created_at=c.created_at
        ))

    return ClauseExtractionResponse(
        document_id=document_id,
        clauses_extracted=len(clause_responses),
        clauses=clause_responses,
        message=f"Successfully extracted {len(clause_responses)} clauses"
    )


@router.get(
    "/documents/{document_id}/clauses",
    response_model=ClauseListResponse
)
def list_clauses(
    document_id: UUID,
    clause_type: Optional[str] = Query(
        None, description="Filter by clause type"),
    min_risk_score: Optional[float] = Query(
        None, description="Minimum risk score"),
    max_risk_score: Optional[float] = Query(
        None, description="Maximum risk score"),
    has_risk_flags: Optional[bool] = Query(
        None, description="Only clauses with risk flags"),
    page_number: Optional[int] = Query(
        None, description="Filter by page number"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all clauses for a document with optional filtering.

    Supports filtering by:
    - clause_type: Type of clause
    - min_risk_score / max_risk_score: Risk score range
    - has_risk_flags: Only clauses with risk flags
    - page_number: Specific page
    """
    # Verify document exists
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

    # Build query
    query = db.query(Clause).filter(Clause.document_id == document_id)

    # Apply filters
    if clause_type:
        query = query.filter(Clause.clause_type == clause_type)

    if page_number is not None:
        query = query.filter(Clause.page_number == page_number)

    if has_risk_flags is not None:
        if has_risk_flags:
            # Only clauses with non-empty risk_flags
            # PostgreSQL doesn't support != operator for JSON types directly
            # Use raw SQL text() to compare JSON as text (avoids SQLAlchemy caching issues)
            query = query.filter(Clause.risk_flags.isnot(None))
            # Use raw SQL to compare JSON as text
            query = query.filter(
                text("clauses.risk_flags::text != '[]'")
            )
        else:
            # Only clauses without risk flags
            # Check if NULL or empty array
            query = query.filter(
                (Clause.risk_flags.is_(None)) |
                (text("clauses.risk_flags::text = '[]'"))
            )

    clauses = query.order_by(Clause.page_number, Clause.clause_type).all()

    # Filter by risk score if needed
    filtered_clauses = clauses
    if min_risk_score is not None:
        filtered_clauses = [
            c for c in filtered_clauses if c.risk_score is not None and c.risk_score >= min_risk_score]
    if max_risk_score is not None:
        filtered_clauses = [
            c for c in filtered_clauses if c.risk_score is not None and c.risk_score <= max_risk_score]

    # Convert clauses to response format
    clause_responses = []
    for c in filtered_clauses:
        risk_flags_list = c.risk_flags if c.risk_flags else []
        if not isinstance(risk_flags_list, list):
            risk_flags_list = []

        clause_responses.append(ClauseResponse(
            id=c.id,
            document_id=c.document_id,
            clause_type=c.clause_type,
            extracted_text=c.extracted_text,
            page_number=c.page_number,
            section=c.section,
            confidence_score=c.confidence_score,
            risk_score=c.risk_score or 0.0,
            risk_flags=risk_flags_list,
            risk_reasoning=c.risk_reasoning,
            clause_subtype=c.clause_subtype,
            created_at=c.created_at
        ))

    return ClauseListResponse(
        total=len(clause_responses),
        clauses=clause_responses
    )


@router.get(
    "/clauses/{clause_id}",
    response_model=ClauseResponse
)
def get_clause(
    clause_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific clause by ID (only if document belongs to user)"""
    clause = db.query(Clause).filter(Clause.id == clause_id).first()
    if not clause:
        raise HTTPException(status_code=404, detail="Clause not found")

    # Verify document and workspace belong to user
    document = db.query(Document).filter(
        Document.id == clause.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Clause not found")

    workspace = db.query(Workspace).filter(
        Workspace.id == document.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Clause not found")

    risk_flags_list = clause.risk_flags if clause.risk_flags else []
    if not isinstance(risk_flags_list, list):
        risk_flags_list = []

    return ClauseResponse(
        id=clause.id,
        document_id=clause.document_id,
        clause_type=clause.clause_type,
        extracted_text=clause.extracted_text,
        page_number=clause.page_number,
        section=clause.section,
        confidence_score=clause.confidence_score,
        risk_score=clause.risk_score or 0.0,
        risk_flags=risk_flags_list,
        risk_reasoning=clause.risk_reasoning,
        clause_subtype=clause.clause_subtype,
        created_at=clause.created_at
    )


@router.delete("/clauses/{clause_id}", status_code=204)
def delete_clause(
    clause_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a clause (only if document belongs to user)"""
    clause = db.query(Clause).filter(Clause.id == clause_id).first()
    if not clause:
        raise HTTPException(status_code=404, detail="Clause not found")

    # Verify document and workspace belong to user
    document = db.query(Document).filter(
        Document.id == clause.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Clause not found")

    workspace = db.query(Workspace).filter(
        Workspace.id == document.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Clause not found")

    db.delete(clause)
    db.commit()
    return None
