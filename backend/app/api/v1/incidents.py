from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.incident import Incident, IncidentStatus, IncidentSeverity, IncidentTimeline
from backend.app.models.service import Service, ServiceStatus
from backend.app.schemas.incident import IncidentResponse, IncidentCreateRequest, IncidentTimelineResponse
from backend.app.api.deps import get_current_user, require_role, record_audit
from backend.app.models.user import User, UserRole

router = APIRouter()

@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    status_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    service_slug: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter)
    if severity_filter:
        query = query.filter(Incident.severity == severity_filter)
    if service_slug:
        query = query.join(Service).filter(Service.slug == service_slug)

    incidents = query.order_by(Incident.triggered_at.desc()).all()
    results = []
    for inc in incidents:
        res = IncidentResponse(
            id=inc.id,
            incident_number=inc.incident_number,
            title=inc.title,
            description=inc.description,
            service_id=inc.service_id,
            service_name=inc.service.name if inc.service else None,
            service_slug=inc.service.slug if inc.service else None,
            severity=inc.severity.value,
            status=inc.status.value,
            triggered_at=inc.triggered_at,
            resolved_at=inc.resolved_at,
            root_cause=inc.root_cause,
            assigned_to_email=inc.assigned_to.email if inc.assigned_to else None,
            timeline=[
                IncidentTimelineResponse(
                    id=t.id,
                    timestamp=t.timestamp,
                    title=t.title,
                    description=t.description,
                    entry_type=t.entry_type
                )
                for t in inc.timeline
            ]
        )
        results.append(res)
    return results

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    return IncidentResponse(
        id=inc.id,
        incident_number=inc.incident_number,
        title=inc.title,
        description=inc.description,
        service_id=inc.service_id,
        service_name=inc.service.name if inc.service else None,
        service_slug=inc.service.slug if inc.service else None,
        severity=inc.severity.value,
        status=inc.status.value,
        triggered_at=inc.triggered_at,
        resolved_at=inc.resolved_at,
        root_cause=inc.root_cause,
        assigned_to_email=inc.assigned_to.email if inc.assigned_to else None,
        timeline=[
            IncidentTimelineResponse(
                id=t.id,
                timestamp=t.timestamp,
                title=t.title,
                description=t.description,
                entry_type=t.entry_type
            )
            for t in inc.timeline
        ]
    )

@router.post("/", response_model=IncidentResponse)
def create_incident(
    payload: IncidentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER, UserRole.SECURITY_ANALYST, UserRole.ADMINISTRATOR]))
):
    service = db.query(Service).filter(Service.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    inc_num = f"INC-{db.query(Incident).count() + 4100}"
    incident = Incident(
        incident_number=inc_num,
        title=payload.title,
        description=payload.description,
        service_id=payload.service_id,
        severity=IncidentSeverity(payload.severity),
        status=IncidentStatus.TRIGGERED,
        triggered_at=datetime.utcnow(),
        assigned_to_user_id=current_user.id
    )
    db.add(incident)
    db.flush()

    # Add initial alert to timeline
    t = IncidentTimeline(
        incident_id=incident.id,
        timestamp=datetime.utcnow(),
        title="Incident Manually Created",
        description=f"Created by {current_user.email}: {payload.title}",
        entry_type="ALERT"
    )
    db.add(t)

    # Update service status if severe
    if payload.severity in ["P0", "P1"]:
        service.status = ServiceStatus.CRITICAL
    else:
        service.status = ServiceStatus.DEGRADED

    db.commit()
    record_audit(db, current_user, "INCIDENT_CREATED", "Incident", str(incident.id), {"incident_number": inc_num})
    return get_incident(incident.id, db, current_user)
