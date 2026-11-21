from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.service import Service, Deployment
from backend.app.models.observability import MetricObservation, LogEntry
from backend.app.schemas.service import ServiceResponse, DeploymentResponse
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ServiceResponse])
def list_services(
    tier: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Service)
    if tier:
        query = query.filter(Service.tier == tier)
    if status:
        query = query.filter(Service.status == status)
    
    services = query.order_by(Service.name).all()
    results = []
    for s in services:
        res = ServiceResponse.model_validate(s)
        if s.owner_team:
            res.owner_team_name = s.owner_team.name
        results.append(res)
    return results

@router.get("/{slug}")
def get_service_details(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = db.query(Service).filter(Service.slug == slug).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    recent_deployments = db.query(Deployment).filter(
        Deployment.service_id == service.id
    ).order_by(Deployment.created_at.desc()).limit(5).all()

    latest_metrics = db.query(MetricObservation).filter(
        MetricObservation.service_id == service.id
    ).order_by(MetricObservation.timestamp.desc()).limit(15).all()

    return {
        "service": {
            "id": service.id,
            "name": service.name,
            "slug": service.slug,
            "description": service.description,
            "tier": service.tier.value,
            "status": service.status.value,
            "active_version": service.active_version,
            "owner_team": service.owner_team.name if service.owner_team else None,
            "language": service.language,
            "framework": service.framework,
            "repo_url": service.repo_url,
            "created_at": service.created_at.isoformat(),
            "updated_at": service.updated_at.isoformat()
        },
        "recent_deployments": [
            {
                "id": d.id,
                "version": d.version,
                "environment": d.environment.value,
                "status": d.status.value,
                "risk_score": d.risk_score,
                "deployed_by": d.deployed_by,
                "created_at": d.created_at.isoformat()
            }
            for d in recent_deployments
        ],
        "metrics_series": [
            {
                "timestamp": m.timestamp.isoformat(),
                "error_rate": m.error_rate,
                "latency_p95": m.latency_p95,
                "latency_p99": m.latency_p99,
                "cpu_usage": m.cpu_usage,
                "memory_usage": m.memory_usage,
                "db_latency": m.db_latency
            }
            for m in reversed(latest_metrics)
        ]
    }
