from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.security import SecurityFinding, IAMEvent
from backend.app.models.service import Service
from backend.app.schemas.security import SecurityFindingResponse, IAMEventResponse
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/findings", response_model=List[SecurityFindingResponse])
def list_security_findings(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    service_slug: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SecurityFinding)
    if severity:
        query = query.filter(SecurityFinding.severity == severity.upper())
    if status:
        query = query.filter(SecurityFinding.status == status.upper())
    if service_slug:
        query = query.join(Service).filter(Service.slug == service_slug)

    findings = query.order_by(SecurityFinding.cvss_score.desc()).all()
    results = []
    for f in findings:
        res = SecurityFindingResponse.model_validate(f)
        res.service_name = f.service.name if f.service else None
        results.append(res)
    return results

@router.get("/iam-events", response_model=List[IAMEventResponse])
def list_iam_events(
    suspicious_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(IAMEvent)
    if suspicious_only:
        query = query.filter(IAMEvent.is_suspicious == True)

    events = query.order_by(IAMEvent.timestamp.desc()).limit(limit).all()
    return events
