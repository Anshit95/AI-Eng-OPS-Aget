from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.models.service import Service, ServiceStatus, Deployment
from backend.app.models.incident import Incident, IncidentStatus, IncidentSeverity, IncidentTimeline
from backend.app.models.security import SecurityFinding, FindingStatus, FindingSeverity, IAMEvent
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Service stats
    total_services = db.query(Service).count()
    healthy_services = db.query(Service).filter(Service.status == ServiceStatus.HEALTHY).count()
    degraded_services = db.query(Service).filter(Service.status == ServiceStatus.DEGRADED).count()
    critical_services = db.query(Service).filter(Service.status == ServiceStatus.CRITICAL).count()

    # Active Incidents stats
    active_incidents = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.TRIGGERED, IncidentStatus.INVESTIGATING])
    ).all()
    
    p0_count = sum(1 for i in active_incidents if i.severity == IncidentSeverity.P0)
    p1_count = sum(1 for i in active_incidents if i.severity == IncidentSeverity.P1)
    p2_count = sum(1 for i in active_incidents if i.severity == IncidentSeverity.P2)
    p3_count = sum(1 for i in active_incidents if i.severity == IncidentSeverity.P3)

    # Security stats
    open_vulns = db.query(SecurityFinding).filter(SecurityFinding.status == FindingStatus.OPEN).all()
    critical_vulns = sum(1 for v in open_vulns if v.severity == FindingSeverity.CRITICAL)
    high_vulns = sum(1 for v in open_vulns if v.severity == FindingSeverity.HIGH)
    suspicious_iam = db.query(IAMEvent).filter(IAMEvent.is_suspicious == True).count()

    # Deployments
    recent_deployments = db.query(Deployment).order_by(Deployment.created_at.desc()).limit(5).all()
    avg_risk = db.query(func.avg(Deployment.risk_score)).scalar() or 0.0

    # System Health Score calculation (0 - 100%)
    deductions = (critical_services * 30) + (degraded_services * 15) + (p0_count * 25) + (critical_vulns * 10)
    health_score = max(5.0, min(100.0, 100.0 - deductions))

    # Recent activity
    recent_events = db.query(IncidentTimeline).order_by(IncidentTimeline.timestamp.desc()).limit(8).all()

    return {
        "health_score": round(health_score, 1),
        "services": {
            "total": total_services,
            "healthy": healthy_services,
            "degraded": degraded_services,
            "critical": critical_services
        },
        "incidents": {
            "total_active": len(active_incidents),
            "p0": p0_count,
            "p1": p1_count,
            "p2": p2_count,
            "p3": p3_count
        },
        "security": {
            "open_vulnerabilities": len(open_vulns),
            "critical_cves": critical_vulns,
            "high_cves": high_vulns,
            "suspicious_iam_events": suspicious_iam
        },
        "deployments": {
            "recent_count": len(recent_deployments),
            "avg_risk_score": round(float(avg_risk), 2)
        },
        "recent_activity": [
            {
                "id": ev.id,
                "timestamp": ev.timestamp.isoformat(),
                "title": ev.title,
                "description": ev.description,
                "type": ev.entry_type,
                "incident_id": ev.incident_id
            }
            for ev in recent_events
        ]
    }
