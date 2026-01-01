"""Export API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from io import BytesIO

from src.core.database import get_db
from src.core.auth import get_current_user
from src.core.exceptions import NotFoundError
from src.core.logging_config import get_logger
from src.models.conversation import Conversation, ConversationMessage
from src.models.clause import Clause
from src.models.document import Document
from src.models.workspace import Workspace
from src.models.user import User
from src.services.evidence_pack_generator import EvidencePackGenerator
from src.services.export_service import ExportService
from src.schemas.conversation import CitationResponse

router = APIRouter()
evidence_generator = EvidencePackGenerator()
export_service = ExportService()
logger = get_logger(__name__)


@router.get("/conversations/{conversation_id}/messages/{message_id}/evidence-pack")
def download_evidence_pack(
    conversation_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download evidence pack PDF for a specific Q&A message.
    
    Args:
        conversation_id: Conversation UUID
        message_id: Message UUID (the assistant message with answer)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PDF evidence pack
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace.has(user_id=current_user.id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get the message
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == message_id,
        ConversationMessage.conversation_id == conversation_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.role != "assistant":
        raise HTTPException(
            status_code=400,
            detail="Evidence pack can only be generated for assistant messages"
        )
    
    # Get the previous user message (the question)
    user_message = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id,
        ConversationMessage.role == "user",
        ConversationMessage.created_at < message.created_at
    ).order_by(ConversationMessage.created_at.desc()).first()
    
    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Question not found for this answer"
        )
    
    # Parse citations from message
    citations = []
    if message.citations:
        citations_data = message.citations
        for cit_data in citations_data:
            if isinstance(cit_data, dict):
                citations.append(CitationResponse(**cit_data))
            else:
                citations.append(cit_data)
    
    # Generate evidence pack
    try:
        pdf_content = evidence_generator.generate_evidence_pack(
            question=user_message.content,
            answer=message.content,
            citations=citations,
            workspace_name=conversation.workspace.name,
            conversation_title=conversation.title,
        )
        
        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="evidence-pack-{message_id.hex[:8]}.pdf"'
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate evidence pack: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate evidence pack: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/evidence-pack")
def download_conversation_evidence_pack(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download evidence pack PDF for an entire conversation.
    Includes all Q&A pairs in the conversation.
    
    Args:
        conversation_id: Conversation UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PDF evidence pack for entire conversation
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace.has(user_id=current_user.id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get all messages in the conversation
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.message_index).all()
    
    if not messages:
        raise HTTPException(
            status_code=404,
            detail="No messages found in this conversation"
        )
    
    # Convert messages to dict format
    messages_data = []
    for msg in messages:
        citations = msg.citations if msg.citations else []
        messages_data.append({
            "role": msg.role,
            "content": msg.content,
            "citations": citations,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        })
    
    # Generate evidence pack
    try:
        pdf_content = evidence_generator.generate_conversation_evidence_pack(
            conversation_messages=messages_data,
            workspace_name=conversation.workspace.name,
            conversation_title=conversation.title,
        )
        
        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="conversation-evidence-pack-{conversation_id.hex[:8]}.pdf"'
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate conversation evidence pack: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate evidence pack: {str(e)}"
        )


@router.get("/documents/{document_id}/clauses/export")
def export_clauses(
    document_id: UUID,
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export clauses for a document in JSON or CSV format.
    
    Args:
        document_id: Document UUID
        format: Export format (json or csv)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Exported clauses file
    """
    # Verify document exists and belongs to user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.workspace.has(user_id=current_user.id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get all clauses for the document
    clauses = db.query(Clause).filter(Clause.document_id == document_id).all()
    
    if not clauses:
        raise HTTPException(
            status_code=404,
            detail="No clauses found for this document"
        )
    
    try:
        if format == "json":
            content = export_service.export_clauses_json(clauses)
            media_type = "application/json"
            filename = f"clauses-{document.name}-{document_id.hex[:8]}.json"
        else:  # csv
            content = export_service.export_clauses_csv(clauses)
            media_type = "text/csv"
            filename = f"clauses-{document.name}-{document_id.hex[:8]}.csv"
        
        return StreamingResponse(
            BytesIO(content),
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        logger.error(f"Failed to export clauses: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export clauses: {str(e)}"
        )


@router.get("/documents/{document_id}/review-checklist")
def export_review_checklist(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download PDF review checklist for a document.
    
    Args:
        document_id: Document UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PDF review checklist
    """
    # Verify document exists and belongs to user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.workspace.has(user_id=current_user.id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get all clauses for the document with document relationship loaded
    clauses = db.query(Clause).options(joinedload(Clause.document)).filter(Clause.document_id == document_id).all()
    
    if not clauses:
        raise HTTPException(
            status_code=404,
            detail="No clauses found for this document"
        )
    
    try:
        pdf_content = export_service.export_review_checklist_pdf(
            clauses=clauses,
            document_name=document.name
        )
        
        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="review-checklist-{document.name}-{document_id.hex[:8]}.pdf"'
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate review checklist: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate review checklist: {str(e)}"
        )


@router.get("/documents/{document_id}/highlighted-contract")
def export_highlighted_contract(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export contract PDF with highlighted risky clauses.
    
    Args:
        document_id: Document UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Highlighted PDF contract
    """
    # Verify document exists and belongs to user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.workspace.has(user_id=current_user.id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if document is PDF
    if document.file_type.value != "pdf":
        raise HTTPException(
            status_code=400,
            detail="Highlighted export is only available for PDF documents"
        )
    
    # Get all clauses for the document with document relationship loaded
    clauses = db.query(Clause).options(joinedload(Clause.document)).filter(Clause.document_id == document_id).all()
    
    if not clauses:
        raise HTTPException(
            status_code=404,
            detail="No clauses found for this document"
        )
    
    # Check if file exists
    from pathlib import Path
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document file not found"
        )
    
    try:
        pdf_content = export_service.export_highlighted_contract_pdf(
            document_path=str(file_path),
            clauses=clauses
        )
        
        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="highlighted-{document.name}"'
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate highlighted contract: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate highlighted contract: {str(e)}"
        )

