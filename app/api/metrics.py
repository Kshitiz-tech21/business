
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models.base import Metric, WorkspaceMember, User
from ..core.config import settings
from ..core.security import get_current_user # Assume this is implemented in auth.py

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.post("/", status_code=201)
def create_metric(
    workspace_id: UUID, name: str, formula_sql: str, aggregation_type: str, unit: str,
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member or member.role not in ["OWNER", "ADMIN", "EDITOR"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    metric = Metric(
        workspace_id=workspace_id,
        name=name,
        formula_sql=formula_sql,
        aggregation_type=aggregation_type,
        unit=unit
    )
    session.add(metric)
    session.commit()
    session.refresh(metric)
    return metric

@router.get("/")
def list_metrics(
    workspace_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return session.exec(select(Metric).where(Metric.workspace_id == workspace_id)).all()
