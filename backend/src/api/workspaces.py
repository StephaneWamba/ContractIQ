from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_serializer
from typing import List
from datetime import datetime

from src.core.database import get_db
from src.models.workspace import Workspace

router = APIRouter()


class WorkspaceCreate(BaseModel):
    name: str
    is_temporary: bool = True


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    is_temporary: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db)):
    """Create a new workspace"""
    db_workspace = Workspace(name=workspace.name, is_temporary=workspace.is_temporary)
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace


@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(db: Session = Depends(get_db)):
    """List all workspaces"""
    workspaces = db.query(Workspace).all()
    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, db: Session = Depends(get_db)):
    """Get a workspace by ID"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str, db: Session = Depends(get_db)):
    """Delete a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.delete(workspace)
    db.commit()
    return {"message": "Workspace deleted"}

