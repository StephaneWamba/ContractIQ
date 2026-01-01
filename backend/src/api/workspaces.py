"""Workspace API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.core.database import get_db
from src.core.auth import get_current_user
from src.core.exceptions import NotFoundError
from src.core.logging_config import get_logger
from src.core.cache import cache_service
from src.core.config import settings
from src.models.workspace import Workspace
from src.models.user import User
from src.schemas.workspace import WorkspaceCreate, WorkspaceResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=WorkspaceResponse, status_code=201)
def create_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace for the current user"""
    db_workspace = Workspace(
        user_id=current_user.id,
        name=workspace.name,
        description=workspace.description,
        is_temporary=workspace.is_temporary
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    
    # Invalidate user workspaces cache
    cache_service.delete(f"user:{current_user.id}:workspaces")
    
    # Convert SQLAlchemy model to Pydantic response model
    return WorkspaceResponse.model_validate(db_workspace)


@router.get("/", response_model=List[WorkspaceResponse])
def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workspaces for the current user"""
    cache_key = f"user:{current_user.id}:workspaces"
    
    # Try cache first
    cached = cache_service.get(cache_key)
    if cached is not None:
        # Convert cached dicts back to Pydantic models
        return [WorkspaceResponse.model_validate(w) if isinstance(w, dict) else w for w in cached]
    
    # Query database
    workspaces = db.query(Workspace).filter(Workspace.user_id == current_user.id).all()
    
    # Convert SQLAlchemy models to Pydantic response models
    # Pydantic v2 uses model_validate instead of from_orm
    result = [WorkspaceResponse.model_validate(w) for w in workspaces]
    
    # Cache result as JSON-serializable dicts (5 minutes)
    # Use mode='json' to ensure proper serialization
    cache_service.set(cache_key, [w.model_dump(mode='json') for w in result], ttl=300)
    
    return result


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workspace (only if owned by current user)"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise NotFoundError("workspace", str(workspace_id))
    
    # Convert SQLAlchemy model to Pydantic response model
    return WorkspaceResponse.model_validate(workspace)


@router.delete("/{workspace_id}", status_code=204)
def delete_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workspace (only if owned by current user)"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    if not workspace:
        raise NotFoundError("workspace", str(workspace_id))
    
    logger.info(
        f"Deleting workspace",
        extra={"workspace_id": str(workspace_id), "user_id": str(current_user.id)}
    )
    
    db.delete(workspace)
    db.commit()
    
    # Invalidate all workspace-related caches
    cache_service.invalidate_workspace(str(workspace_id))
    cache_service.delete(f"user:{current_user.id}:workspaces")
    
    return None

