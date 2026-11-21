from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.observability import MetricObservation, LogEntry
from backend.app.models.service import Service
from backend.app.schemas.observability import MetricObservationResponse, LogEntryResponse
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/metrics", response_model=List[MetricObservationResponse])
def get_metrics(
    service_slug: Optional[str] = None,
    service_id: Optional[int] = None,
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(MetricObservation)
    if service_slug:
        query = query.join(Service).filter(Service.slug == service_slug)
    elif service_id:
        query = query.filter(MetricObservation.service_id == service_id)

    metrics = query.order_by(MetricObservation.timestamp.desc()).limit(limit).all()
    return list(reversed(metrics))

@router.get("/logs", response_model=List[LogEntryResponse])
def get_logs(
    service_slug: Optional[str] = None,
    service_id: Optional[int] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    trace_id: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(LogEntry)
    if service_slug:
        query = query.join(Service).filter(Service.slug == service_slug)
    elif service_id:
        query = query.filter(LogEntry.service_id == service_id)

    if level:
        query = query.filter(LogEntry.level == level.upper())
    if trace_id:
        query = query.filter(LogEntry.trace_id == trace_id)
    if search:
        query = query.filter(LogEntry.message.ilike(f"%{search}%"))

    logs = query.order_by(LogEntry.timestamp.desc()).limit(limit).all()
    return logs
