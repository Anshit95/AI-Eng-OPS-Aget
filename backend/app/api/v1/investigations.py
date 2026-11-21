import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.investigation import Investigation
from backend.app.schemas.investigation import InvestigationResponse, InvestigationCreateRequest
from backend.app.api.deps import get_current_user, require_role, record_audit
from backend.app.models.user import User, UserRole
from backend.app.agent.orchestrator import InvestigationOrchestrator

router = APIRouter()

@router.get("/", response_model=List[InvestigationResponse])
def list_investigations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investigations = db.query(Investigation).order_by(Investigation.created_at.desc()).all()
    results = []
    for inv in investigations:
        res = InvestigationResponse(
            id=inv.id,
            incident_id=inv.incident_id,
            incident_number=inv.incident.incident_number if inv.incident else None,
            service_name=inv.incident.service.name if inv.incident and inv.incident.service else None,
            status=inv.status.value,
            summary=inv.summary,
            root_cause_hypotheses=json.loads(inv.root_cause_hypotheses_json or "[]"),
            evidence_citations=json.loads(inv.evidence_citations_json or "[]"),
            recommendations=json.loads(inv.recommendations_json or "[]"),
            confidence_score=inv.confidence_score,
            token_usage=json.loads(inv.token_usage_json or "{}"),
            created_at=inv.created_at,
            updated_at=inv.updated_at
        )
        results.append(res)
    return results

@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    return InvestigationResponse(
        id=inv.id,
        incident_id=inv.incident_id,
        incident_number=inv.incident.incident_number if inv.incident else None,
        service_name=inv.incident.service.name if inv.incident and inv.incident.service else None,
        status=inv.status.value,
        summary=inv.summary,
        root_cause_hypotheses=json.loads(inv.root_cause_hypotheses_json or "[]"),
        evidence_citations=json.loads(inv.evidence_citations_json or "[]"),
        recommendations=json.loads(inv.recommendations_json or "[]"),
        confidence_score=inv.confidence_score,
        token_usage=json.loads(inv.token_usage_json or "{}"),
        created_at=inv.created_at,
        updated_at=inv.updated_at
    )

@router.post("/", response_model=InvestigationResponse)
def create_investigation(
    payload: InvestigationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER, UserRole.SECURITY_ANALYST, UserRole.ADMINISTRATOR]))
):
    orchestrator = InvestigationOrchestrator(db, user_role=current_user.role.value)
    result = orchestrator.run_investigation(payload.incident_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    record_audit(
        db, current_user, "INVESTIGATION_INITIATED", "Investigation", str(result["investigation_id"]),
        {"incident_id": payload.incident_id}
    )
    return get_investigation(result["investigation_id"], db, current_user)
