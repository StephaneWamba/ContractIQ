"""Conversation and Q&A API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4

from src.core.database import get_db
from src.core.auth import get_current_user
from src.core.exceptions import NotFoundError, ProcessingError
from src.core.logging_config import get_logger
from src.models.conversation import Conversation, ConversationMessage
from src.models.workspace import Workspace
from src.models.user import User
from src.schemas.conversation import (
    ConversationResponse,
    MessageResponse,
    AskQuestionRequest,
    AskQuestionResponse,
    ConversationListResponse,
    CitationResponse,
    ConversationUpdate
)
from src.services.rag_pipeline import RAGPipeline

router = APIRouter()
rag_pipeline = RAGPipeline()
logger = get_logger(__name__)


@router.post(
    "/workspaces/{workspace_id}/conversations",
    response_model=ConversationResponse,
    status_code=201
)
def create_conversation(
    workspace_id: UUID,
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.
    
    Args:
        workspace_id: Workspace UUID
        title: Optional conversation title
        db: Database session
        
    Returns:
        Created conversation
    """
    # Verify workspace exists and belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise NotFoundError("workspace", str(workspace_id))
    
    # Create conversation
    conversation = Conversation(
        workspace_id=workspace_id,
        title=title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        workspace_id=conversation.workspace_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[]
    )


@router.get(
    "/workspaces/{workspace_id}/conversations",
    response_model=ConversationListResponse
)
def list_conversations(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations in a workspace (only if workspace belongs to user)"""
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    conversations = db.query(Conversation).filter(
        Conversation.workspace_id == workspace_id
    ).order_by(Conversation.updated_at.desc()).all()
    
    conversation_responses = []
    for conv in conversations:
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conv.id
        ).order_by(ConversationMessage.message_index).all()
        
        # Convert messages with citations
        message_responses = []
        for m in messages:
            citations = None
            if m.citations:
                citations = [CitationResponse(**c) if isinstance(c, dict) else c for c in m.citations]
            
            msg_resp = MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                citations=citations,
                message_index=m.message_index,
                created_at=m.created_at
            )
            message_responses.append(msg_resp)
        
        conversation_responses.append(ConversationResponse(
            id=conv.id,
            workspace_id=conv.workspace_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=message_responses
        ))
    
    return ConversationListResponse(
        total=len(conversation_responses),
        conversations=conversation_responses
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse
)
def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages (only if workspace belongs to user)"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == conversation.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.message_index).all()
    
    # Convert messages with citations
    message_responses = []
    for m in messages:
        citations = None
        if m.citations:
            citations = [CitationResponse(**c) if isinstance(c, dict) else c for c in m.citations]
        
        msg_resp = MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            citations=citations,
            message_index=m.message_index,
            created_at=m.created_at
        )
        message_responses.append(msg_resp)
    
    return ConversationResponse(
        id=conversation.id,
        workspace_id=conversation.workspace_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_responses
    )


@router.post(
    "/conversations/{conversation_id}/ask",
    response_model=AskQuestionResponse,
    status_code=200
)
def ask_question(
    conversation_id: UUID,
    request: AskQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask a question in a conversation (only if workspace belongs to user).
    
    This endpoint:
    1. Retrieves conversation history
    2. Runs RAG pipeline to get answer
    3. Stores user question and assistant answer
    4. Returns answer with citations
    """
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise NotFoundError("conversation", str(conversation_id))
    
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == conversation.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise NotFoundError("conversation", str(conversation_id))
    
    # Get conversation history
    existing_messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.message_index).all()
    
    conversation_history = []
    for msg in existing_messages:
        # Parse citations from JSON (already stored as list of dicts)
        citations = None
        if msg.citations:
            # Citations are already stored as JSON (list of dicts)
            citations = msg.citations
        
        conversation_history.append({
            "role": msg.role,
            "content": msg.content,
            "citations": citations
        })
    
    # Get next message index
    next_index = len(existing_messages)
    
    # Store user question
    user_message = ConversationMessage(
        conversation_id=conversation_id,
        role="user",
        content=request.question,
        message_index=next_index,
        citations=None
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Run RAG pipeline
    try:
        result = rag_pipeline.ask(
            question=request.question,
            workspace_id=str(conversation.workspace_id),
            document_ids=request.document_ids,
            conversation_history=conversation_history
        )
        
        # Store assistant answer
        assistant_message = ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=result["answer"],
            message_index=next_index + 1,
            citations=[c for c in result["citations"]]  # Store as JSON
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        from datetime import datetime
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(assistant_message)
        
        # Convert citations to response format
        citations_response = []
        for c in result["citations"]:
            if isinstance(c, dict):
                citations_response.append(CitationResponse(**c))
            else:
                citations_response.append(c)
        
        return AskQuestionResponse(
            answer=result["answer"],
            citations=citations_response,
            message_id=assistant_message.id,
            conversation_id=conversation_id,
            retrieved_chunks_count=result.get("retrieved_chunks_count", 0)
        )
        
    except Exception as e:
        logger.error(
            f"Error processing question in conversation {conversation_id}",
            extra={
                "conversation_id": str(conversation_id),
                "workspace_id": str(conversation.workspace_id),
                "question": request.question[:100] if request.question else None,
                "error": str(e)
            },
            exc_info=True
        )
        
        # Store error message
        error_message = ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content="I apologize, but I encountered an error while processing your question. Please try again.",
            message_index=next_index + 1,
            citations=None
        )
        db.add(error_message)
        db.commit()
        
        raise ProcessingError(
            message=f"Failed to process question: {str(e)}",
            stage="rag_pipeline",
            user_message="I encountered an error while processing your question. Please try again in a moment."
        ) from e


@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse
)
def update_conversation(
    conversation_id: UUID,
    update: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a conversation (currently only title) - only if workspace belongs to user"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == conversation.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if update.title is not None:
        conversation.title = update.title
        from datetime import datetime
        conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(conversation)
    
    # Get messages
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.message_index).all()
    
    message_responses = []
    for m in messages:
        citations = None
        if m.citations:
            citations = [CitationResponse(**c) if isinstance(c, dict) else c for c in m.citations]
        
        msg_resp = MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            citations=citations,
            message_index=m.message_index,
            created_at=m.created_at
        )
        message_responses.append(msg_resp)
    
    return ConversationResponse(
        id=conversation.id,
        workspace_id=conversation.workspace_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_responses
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Messages will be deleted via cascade
    db.delete(conversation)
    db.commit()
    return None

