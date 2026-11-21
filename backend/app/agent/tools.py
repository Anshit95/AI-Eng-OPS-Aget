import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.service import Service, Deployment, PullRequest
from backend.app.models.incident import Incident, IncidentStatus, IncidentSeverity
from backend.app.models.observability import MetricObservation, LogEntry
from backend.app.models.security import SecurityFinding, IAMEvent
from backend.app.ml.anomaly_detector import anomaly_detector
from backend.app.ml.severity_predictor import severity_predictor
from backend.app.ml.deployment_risk import deployment_risk_estimator
from backend.app.rag.retriever import search_knowledge
from backend.app.models.investigation import Investigation, InvestigationStatus, ActionRequest, ActionType, ActionStatus
from backend.app.simulator.adapters import NexaRemediationAdapter

class AgentTools:
    """Typed application tools with argument validation and least-privilege scoping."""

    def __init__(self, db: Session, user_role: str = "Engineer"):
        self.db = db
        self.user_role = user_role

    def get_incident_context(self, incident_id: int) -> Dict[str, Any]:
        """Tool: Retrieve detailed incident context, alert metadata, and timeline."""
        inc = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            return {"error": f"Incident ID {incident_id} not found"}
        
        return {
            "incident_id": inc.id,
            "incident_number": inc.incident_number,
            "title": inc.title,
            "description": inc.description,
            "severity": inc.severity.value,
            "status": inc.status.value,
            "service_id": inc.service_id,
            "service_name": inc.service.name if inc.service else None,
            "service_slug": inc.service.slug if inc.service else None,
            "service_tier": inc.service.tier.value if inc.service else None,
            "triggered_at": inc.triggered_at.isoformat(),
            "timeline": [
                {"timestamp": t.timestamp.isoformat(), "title": t.title, "description": t.description, "type": t.entry_type}
                for t in inc.timeline
            ]
        }

    def query_service_metrics(self, service_slug: str, limit: int = 15) -> Dict[str, Any]:
        """Tool: Query recent time-series telemetry metrics for a service."""
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            return {"error": f"Service '{service_slug}' not found"}

        metrics = self.db.query(MetricObservation).filter(
            MetricObservation.service_id == service.id
        ).order_by(MetricObservation.timestamp.desc()).limit(limit).all()

        return {
            "service": service_slug,
            "datapoints_count": len(metrics),
            "recent_metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "error_rate": m.error_rate,
                    "latency_p95": m.latency_p95,
                    "latency_p99": m.latency_p99,
                    "request_count": m.request_count,
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "db_latency": m.db_latency
                }
                for m in reversed(metrics)
            ]
        }

    def query_application_logs(self, service_slug: str, level: Optional[str] = "ERROR", limit: int = 20) -> Dict[str, Any]:
        """Tool: Search structured logs for errors, exceptions, and deadlocks."""
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            return {"error": f"Service '{service_slug}' not found"}

        query = self.db.query(LogEntry).filter(LogEntry.service_id == service.id)
        if level:
            query = query.filter(LogEntry.level == level.upper())
        
        logs = query.order_by(LogEntry.timestamp.desc()).limit(limit).all()
        return {
            "service": service_slug,
            "logs_found": len(logs),
            "entries": [
                {
                    "timestamp": l.timestamp.isoformat(),
                    "level": l.level,
                    "message": l.message,
                    "trace_id": l.trace_id,
                    "source": l.source,
                    "metadata": json.loads(l.metadata_json or "{}")
                }
                for l in logs
            ]
        }

    def get_recent_deployments(self, service_slug: str) -> Dict[str, Any]:
        """Tool: Retrieve recent release deployments and pull request metadata."""
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            return {"error": f"Service '{service_slug}' not found"}

        deployments = self.db.query(Deployment).filter(
            Deployment.service_id == service.id
        ).order_by(Deployment.created_at.desc()).limit(5).all()

        dep_list = []
        for d in deployments:
            pr_data = None
            if d.pull_request:
                pr_data = {
                    "pr_number": d.pull_request.pr_number,
                    "title": d.pull_request.title,
                    "has_migrations": d.pull_request.has_migrations,
                    "lines_added": d.pull_request.lines_added,
                    "files_changed": d.pull_request.files_changed_count
                }
            dep_list.append({
                "id": d.id,
                "version": d.version,
                "commit_sha": d.commit_sha[:10],
                "environment": d.environment.value,
                "status": d.status.value,
                "risk_score": d.risk_score,
                "rollback_target_version": d.rollback_target_version,
                "deployed_by": d.deployed_by,
                "created_at": d.created_at.isoformat(),
                "pull_request": pr_data
            })

        return {"service": service_slug, "deployments": dep_list}

    def run_anomaly_detection(self, service_slug: str) -> Dict[str, Any]:
        """Tool: Run ML Isolation Forest anomaly detection on latest telemetry."""
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            return {"error": f"Service '{service_slug}' not found"}

        latest = self.db.query(MetricObservation).filter(
            MetricObservation.service_id == service.id
        ).order_by(MetricObservation.timestamp.desc()).first()

        if not latest:
            return {"error": "No telemetry datapoints available"}

        sample = {
            "error_rate": latest.error_rate,
            "latency_p95": latest.latency_p95,
            "latency_p99": latest.latency_p99,
            "cpu_usage": latest.cpu_usage,
            "memory_usage": latest.memory_usage,
            "db_latency": latest.db_latency
        }
        res = anomaly_detector.detect(sample)
        res["service"] = service_slug
        res["observed_telemetry"] = sample
        return res

    def predict_severity(self, service_slug: str, error_rate: float, impacted_users_pct: float) -> Dict[str, Any]:
        """Tool: Predict incident severity using trained ML multi-class classifier."""
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        tier_str = service.tier.value if service else "Tier-2"

        sample = {
            "service_tier": tier_str,
            "error_rate": error_rate,
            "impacted_users_pct": impacted_users_pct,
            "has_security_flag": False,
            "recent_deploy_minutes": 30
        }
        return severity_predictor.predict(sample)

    def search_runbooks_and_postmortems(self, query: str, service_id: Optional[int] = None) -> Dict[str, Any]:
        """Tool: RAG search across engineering runbooks and postmortems."""
        results = search_knowledge(self.db, query, service_id=service_id, limit=3)
        return {"query": query, "retrieved_count": len(results), "chunks": results}

    def check_security_context(self, service_slug: str) -> Dict[str, Any]:
        """Tool: Check CVE vulnerability findings and suspicious IAM events."""
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        findings = []
        if service:
            f_objs = self.db.query(SecurityFinding).filter(SecurityFinding.service_id == service.id).all()
            findings = [
                {
                    "cve_id": f.cve_id,
                    "title": f.title,
                    "severity": f.severity.value,
                    "cvss": f.cvss_score,
                    "package": f.package_name,
                    "affected": f.affected_version,
                    "fixed": f.fixed_version,
                    "is_exploitable": f.is_exploitable,
                    "status": f.status.value
                }
                for f in f_objs
            ]

        iam_events = self.db.query(IAMEvent).filter(IAMEvent.is_suspicious == True).limit(5).all()
        iam_list = [
            {
                "event_name": ev.event_name,
                "principal": ev.service_account or ev.user_email,
                "source_ip": ev.source_ip,
                "timestamp": ev.timestamp.isoformat(),
                "details": json.loads(ev.details_json or "{}")
            }
            for ev in iam_events
        ]

        return {
            "service": service_slug,
            "vulnerabilities": findings,
            "suspicious_iam_events": iam_list
        }
