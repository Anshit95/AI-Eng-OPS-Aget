import random
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.user import User, Team, UserRole
from backend.app.models.service import (
    Service, ServiceTier, ServiceStatus, Repository, Commit, PullRequest,
    Deployment, DeploymentEnvironment, DeploymentStatus
)
from backend.app.models.observability import MetricObservation, LogEntry
from backend.app.models.incident import Incident, IncidentTimeline, IncidentSeverity, IncidentStatus
from backend.app.models.security import SecurityFinding, IAMEvent, FindingSeverity, FindingStatus
from backend.app.models.knowledge import Document, DocumentChunk, DocumentCategory
from backend.app.models.investigation import (
    Investigation, InvestigationStatus, ActionRequest, ActionType, ActionStatus, AuditLog
)

class NexaTechSimulator:
    """
    Fictional enterprise software company simulator.
    Generates relationally consistent, reproducible enterprise operational data
    including 5 specific evaluation scenarios (A, B, C, D, E).
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.now = datetime.utcnow()

    def generate_all(self, db: Session):
        print(f"[*] Starting NexaTech data generation with seed {self.seed}...")
        teams = self._generate_teams(db)
        users = self._generate_users(db, teams)
        services = self._generate_services(db, teams)
        repos, commits, prs = self._generate_code_artifacts(db, services)
        deployments = self._generate_deployments(db, services, prs, commits)
        self._generate_observability(db, services)
        self._generate_security(db, services)
        self._generate_documents(db, services)
        self._generate_incidents(db, services, users, deployments)
        db.commit()
        print("[+] NexaTech data generation completed successfully!")

    def _generate_teams(self, db: Session) -> dict:
        team_defs = [
            ("Core Platform", "Infrastructure, Kubernetes, and developer platform", "platform-lead@nexatech.internal"),
            ("Payments & Billing", "Checkout, payment gateways, and fraud protection", "payments-lead@nexatech.internal"),
            ("Identity & Security", "AuthN, AuthZ, IAM, and security monitoring", "secops-lead@nexatech.internal"),
            ("Order & Fulfillment", "Order lifecycle, catalog, and inventory sync", "orders-lead@nexatech.internal")
        ]
        teams = {}
        for name, desc, lead in team_defs:
            team = db.query(Team).filter(Team.name == name).first()
            if not team:
                team = Team(name=name, description=desc, lead_email=lead)
                db.add(team)
                db.flush()
            teams[name] = team
        return teams

    def _generate_users(self, db: Session, teams: dict) -> list:
        user_defs = [
            ("admin@nexatech.internal", "Admin User", UserRole.ADMINISTRATOR, "Core Platform"),
            ("lead.engineer@nexatech.internal", "Alex Vance", UserRole.ENGINEER, "Payments & Billing"),
            ("sec.analyst@nexatech.internal", "Jordan Reed", UserRole.SECURITY_ANALYST, "Identity & Security"),
            ("ops.viewer@nexatech.internal", "Taylor Morgan", UserRole.VIEWER, "Order & Fulfillment"),
            ("svc-deploy-worker@nexatech.internal", "CI Service Account", UserRole.ENGINEER, "Core Platform")
        ]
        users = []
        default_pwd_hash = hash_password("NexaTech2026!Secure")
        for email, full_name, role, team_name in user_defs:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    full_name=full_name,
                    hashed_password=default_pwd_hash,
                    role=role,
                    team_id=teams[team_name].id,
                    is_active=True
                )
                db.add(user)
                db.flush()
            users.append(user)
        return users

    def _generate_services(self, db: Session, teams: dict) -> dict:
        service_defs = [
            ("payments-service", "payments-service", "Critical payment processing API", ServiceTier.TIER_1, ServiceStatus.CRITICAL, "Payments & Billing", "Python", "FastAPI", "v2.4.2"),
            ("auth-service", "auth-service", "User authentication and JWT token issuer", ServiceTier.TIER_1, ServiceStatus.DEGRADED, "Identity & Security", "Python", "FastAPI", "v1.8.0"),
            ("order-processing", "order-processing", "Order placement and event bus processing", ServiceTier.TIER_2, ServiceStatus.DEGRADED, "Order & Fulfillment", "Python", "FastAPI", "v3.1.0-rc1"),
            ("notification-service", "notification-service", "Email, SMS, and webhook delivery", ServiceTier.TIER_3, ServiceStatus.HEALTHY, "Core Platform", "Python", "FastAPI", "v1.4.5"),
            ("catalog-service", "catalog-service", "Product catalog and inventory caching", ServiceTier.TIER_2, ServiceStatus.HEALTHY, "Order & Fulfillment", "Python", "FastAPI", "v2.1.0")
        ]
        services = {}
        for name, slug, desc, tier, status, team_name, lang, framework, version in service_defs:
            srv = db.query(Service).filter(Service.slug == slug).first()
            if not srv:
                srv = Service(
                    name=name,
                    slug=slug,
                    description=desc,
                    tier=tier,
                    status=status,
                    owner_team_id=teams[team_name].id,
                    repo_url=f"https://github.com/nexatech/{slug}",
                    language=lang,
                    framework=framework,
                    active_version=version
                )
                db.add(srv)
                db.flush()
            services[slug] = srv
        return services

    def _generate_code_artifacts(self, db: Session, services: dict):
        repos = {}
        commits = {}
        prs = {}
        
        # 1. payments-service repo
        pay_srv = services["payments-service"]
        repo = db.query(Repository).filter(Repository.service_id == pay_srv.id).first()
        if not repo:
            repo = Repository(name="payments-service-repo", service_id=pay_srv.id)
            db.add(repo)
            db.flush()
        repos["payments"] = repo

        # Scenario A Commit & PR
        c_pay_stable = Commit(
            repo_id=repo.id,
            commit_sha="a1b2c3d4e5f6789012345678901234567890abcd",
            author_email="lead.engineer@nexatech.internal",
            message="feat: payment gateway v2.4.1 release with stable connection pool",
            lines_added=45, lines_deleted=12, files_changed_count=3,
            created_at=self.now - timedelta(days=5)
        )
        c_pay_faulty = Commit(
            repo_id=repo.id,
            commit_sha="e7f8a9b0c1d2e3f4567890123456789012345678",
            author_email="lead.engineer@nexatech.internal",
            message="perf: add locking table query hints for transaction deduplication (PR #412)",
            lines_added=180, lines_deleted=25, files_changed_count=8,
            created_at=self.now - timedelta(hours=3)
        )
        db.add_all([c_pay_stable, c_pay_faulty])
        db.flush()
        commits["pay_stable"] = c_pay_stable
        commits["pay_faulty"] = c_pay_faulty

        pr_pay = PullRequest(
            repo_id=repo.id,
            pr_number=412,
            title="perf: optimize checkout queries with index hints",
            description="Adds transaction row-locking to ensure deduplication. Includes migration 004_tx_lock.",
            author_email="lead.engineer@nexatech.internal",
            status="MERGED",
            head_sha=c_pay_faulty.commit_sha,
            base_sha=c_pay_stable.commit_sha,
            lines_added=180, lines_deleted=25, files_changed_count=8,
            has_migrations=True,
            merged_at=self.now - timedelta(hours=3),
            created_at=self.now - timedelta(hours=8)
        )
        db.add(pr_pay)
        db.flush()
        prs["pay_pr"] = pr_pay

        # 2. auth-service repo
        auth_srv = services["auth-service"]
        repo_auth = db.query(Repository).filter(Repository.service_id == auth_srv.id).first()
        if not repo_auth:
            repo_auth = Repository(name="auth-service-repo", service_id=auth_srv.id)
            db.add(repo_auth)
            db.flush()
        repos["auth"] = repo_auth

        c_auth = Commit(
            repo_id=repo_auth.id,
            commit_sha="b2c3d4e5f6a1789012345678901234567890ef01",
            author_email="sec.analyst@nexatech.internal",
            message="chore(deps): update token validation dependencies",
            lines_added=15, lines_deleted=10, files_changed_count=2,
            created_at=self.now - timedelta(days=2)
        )
        db.add(c_auth)
        db.flush()
        commits["auth_commit"] = c_auth

        pr_auth = PullRequest(
            repo_id=repo_auth.id,
            pr_number=198,
            title="chore: routine dependency update for auth runtime",
            description="Upgrades core crypto libraries.",
            author_email="sec.analyst@nexatech.internal",
            status="MERGED",
            head_sha=c_auth.commit_sha,
            base_sha="main",
            lines_added=15, lines_deleted=10, files_changed_count=2,
            has_migrations=False,
            merged_at=self.now - timedelta(days=2),
            created_at=self.now - timedelta(days=3)
        )
        db.add(pr_auth)
        db.flush()
        prs["auth_pr"] = pr_auth

        return repos, commits, prs

    def _generate_deployments(self, db: Session, services: dict, prs: dict, commits: dict) -> dict:
        deployments = {}
        pay_srv = services["payments-service"]
        
        # Scenario A: Stable deployment v2.4.1 (target for rollback)
        d_stable = Deployment(
            service_id=pay_srv.id,
            commit_sha=commits["pay_stable"].commit_sha,
            version="v2.4.1",
            environment=DeploymentEnvironment.PRODUCTION,
            status=DeploymentStatus.SUCCESS,
            deployed_by="lead.engineer@nexatech.internal",
            risk_score=0.12,
            rollback_target_version=None,
            created_at=self.now - timedelta(days=5)
        )
        # Faulty deployment v2.4.2 causing regression
        d_faulty = Deployment(
            service_id=pay_srv.id,
            pr_id=prs["pay_pr"].id,
            commit_sha=commits["pay_faulty"].commit_sha,
            version="v2.4.2",
            environment=DeploymentEnvironment.PRODUCTION,
            status=DeploymentStatus.SUCCESS,
            deployed_by="lead.engineer@nexatech.internal",
            risk_score=0.78,
            rollback_target_version="v2.4.1",
            created_at=self.now - timedelta(hours=2, minutes=45)
        )
        db.add_all([d_stable, d_faulty])
        db.flush()
        deployments["pay_stable"] = d_stable
        deployments["pay_faulty"] = d_faulty

        # Scenario D: order-processing canary
        order_srv = services["order-processing"]
        d_order_canary = Deployment(
            service_id=order_srv.id,
            commit_sha="c3d4e5f6a1b2789012345678901234567890bcde",
            version="v3.1.0-rc1",
            environment=DeploymentEnvironment.CANARY,
            status=DeploymentStatus.SUCCESS,
            deployed_by="ops.viewer@nexatech.internal",
            risk_score=0.65,
            rollback_target_version="v3.0.4",
            created_at=self.now - timedelta(hours=4)
        )
        db.add(d_order_canary)
        db.flush()
        deployments["order_canary"] = d_order_canary

        return deployments

    def _generate_observability(self, db: Session, services: dict):
        # 1. payments-service: Baseline before deploy, sharp spike after deploy (Scenario A)
        pay_srv = services["payments-service"]
        for i in range(30):
            ts = self.now - timedelta(minutes=(30 - i) * 6)
            is_post_deploy = (self.now - ts) < timedelta(hours=2, minutes=45)
            
            if is_post_deploy:
                # Regressed state
                obs = MetricObservation(
                    service_id=pay_srv.id,
                    timestamp=ts,
                    error_rate=round(random.uniform(16.5, 22.0), 2),
                    latency_p50=round(random.uniform(450.0, 680.0), 1),
                    latency_p95=round(random.uniform(2200.0, 3100.0), 1),
                    latency_p99=round(random.uniform(3400.0, 4200.0), 1),
                    request_count=random.randint(480, 560),
                    cpu_usage=round(random.uniform(75.0, 92.0), 1),
                    memory_usage=round(random.uniform(65.0, 78.0), 1),
                    db_latency=round(random.uniform(950.0, 1400.0), 1)
                )
                # Correlated error logs
                log = LogEntry(
                    service_id=pay_srv.id,
                    timestamp=ts,
                    level="ERROR",
                    message="DatabaseLockTimeout: deadlock detected on table 'transactions' during row-level acquisition for commit e7f8a9b",
                    trace_id=f"trace-pay-{1000 + i}",
                    span_id=f"span-{i}",
                    source="payment_gateway.db",
                    metadata_json=json.dumps({"version": "v2.4.2", "endpoint": "/api/v1/charge", "http_status": 500})
                )
            else:
                # Normal baseline state
                obs = MetricObservation(
                    service_id=pay_srv.id,
                    timestamp=ts,
                    error_rate=round(random.uniform(0.01, 0.25), 2),
                    latency_p50=round(random.uniform(35.0, 55.0), 1),
                    latency_p95=round(random.uniform(90.0, 140.0), 1),
                    latency_p99=round(random.uniform(180.0, 260.0), 1),
                    request_count=random.randint(450, 520),
                    cpu_usage=round(random.uniform(22.0, 38.0), 1),
                    memory_usage=round(random.uniform(40.0, 48.0), 1),
                    db_latency=round(random.uniform(8.0, 18.0), 1)
                )
                log = LogEntry(
                    service_id=pay_srv.id,
                    timestamp=ts,
                    level="INFO",
                    message="Payment successfully processed via primary PSP token vault",
                    trace_id=f"trace-pay-{1000 + i}",
                    span_id=f"span-{i}",
                    source="payment_gateway.worker",
                    metadata_json=json.dumps({"version": "v2.4.1", "http_status": 200})
                )
            db.add(obs)
            db.add(log)

        # 2. notification-service: Pure Baseline (Scenario E)
        notif_srv = services["notification-service"]
        for i in range(30):
            ts = self.now - timedelta(minutes=(30 - i) * 6)
            obs = MetricObservation(
                service_id=notif_srv.id,
                timestamp=ts,
                error_rate=round(random.uniform(0.01, 0.08), 3),
                latency_p50=round(random.uniform(15.0, 25.0), 1),
                latency_p95=round(random.uniform(45.0, 70.0), 1),
                latency_p99=round(random.uniform(85.0, 130.0), 1),
                request_count=random.randint(120, 180),
                cpu_usage=round(random.uniform(14.0, 26.0), 1),
                memory_usage=round(random.uniform(30.0, 38.0), 1),
                db_latency=round(random.uniform(4.0, 9.0), 1)
            )
            log = LogEntry(
                service_id=notif_srv.id,
                timestamp=ts,
                level="INFO",
                message="Dispatched transactional message to upstream messaging provider",
                trace_id=f"trace-notif-{2000 + i}",
                span_id=f"span-notif-{i}",
                source="notification_worker",
                metadata_json=json.dumps({"provider": "sendgrid_sim", "status": "DELIVERED"})
            )
            db.add(obs)
            db.add(log)

        # 3. order-processing: Memory leak (Scenario D)
        order_srv = services["order-processing"]
        for i in range(30):
            ts = self.now - timedelta(minutes=(30 - i) * 6)
            mem_pct = min(96.0, 42.0 + (i * 1.8))
            obs = MetricObservation(
                service_id=order_srv.id,
                timestamp=ts,
                error_rate=round(min(12.0, max(0.1, (i - 20) * 1.2)), 2),
                latency_p50=round(60.0 + (i * 5), 1),
                latency_p95=round(180.0 + (i * 15), 1),
                latency_p99=round(320.0 + (i * 30), 1),
                request_count=random.randint(220, 310),
                cpu_usage=round(35.0 + (i * 1.5), 1),
                memory_usage=round(mem_pct, 1),
                db_latency=round(18.0 + (i * 1.2), 1)
            )
            level = "WARN" if mem_pct > 75.0 else "INFO"
            if mem_pct > 88.0:
                level = "ERROR"
            msg = f"Memory utilization at {mem_pct:.1f}%. JVM / Async worker heap growth detected."
            log = LogEntry(
                service_id=order_srv.id,
                timestamp=ts,
                level=level,
                message=msg,
                trace_id=f"trace-order-{3000 + i}",
                source="order_executor",
                metadata_json=json.dumps({"version": "v3.1.0-rc1", "canary": True})
            )
            db.add(obs)
            db.add(log)

        db.flush()

    def _generate_security(self, db: Session, services: dict):
        # Scenario B: Vulnerable dependency in auth-service
        auth_srv = services["auth-service"]
        sf = SecurityFinding(
            service_id=auth_srv.id,
            cve_id="CVE-2024-21626",
            title="Critical container breakout / privilege escalation via Leaky Vessels vulnerability",
            description="runc process execution file-descriptor leak allowing container breakout to host filesystem. Auth service is exposed to public network.",
            severity=FindingSeverity.CRITICAL,
            cvss_score=8.6,
            package_name="runc-runtime",
            affected_version="v1.1.11",
            fixed_version="v1.1.12",
            attack_vector="NETWORK",
            is_exploitable=True,
            status=FindingStatus.OPEN,
            created_at=self.now - timedelta(days=1)
        )
        db.add(sf)

        # Non-critical finding in payments
        pay_srv = services["payments-service"]
        sf_pay = SecurityFinding(
            service_id=pay_srv.id,
            cve_id="CVE-2023-44487",
            title="HTTP/2 Rapid Reset Denial of Service Mitigation",
            description="Upstream proxy requires keep-alive request reset rate limiting.",
            severity=FindingSeverity.MEDIUM,
            cvss_score=5.3,
            package_name="hypercorn",
            affected_version="0.14.3",
            fixed_version="0.15.0",
            attack_vector="NETWORK",
            is_exploitable=False,
            status=FindingStatus.RESOLVED,
            created_at=self.now - timedelta(days=14)
        )
        db.add(sf_pay)

        # Scenario C: Suspicious IAM activity
        iam_event_1 = IAMEvent(
            user_email=None,
            service_account="svc-deploy-worker@nexatech.internal",
            event_name="roles.setIamPolicy",
            event_source="iam.googleapis.com",
            source_ip="198.51.100.42",  # External untrusted IP
            is_suspicious=True,
            details_json=json.dumps({
                "granted_role": "roles/resourcemanager.organizationAdmin",
                "target_principal": "svc-deploy-worker@nexatech.internal",
                "reason": "Anomalous role escalation outside deployment window"
            }),
            timestamp=self.now - timedelta(hours=2, minutes=14)
        )
        iam_event_2 = IAMEvent(
            user_email="sec.analyst@nexatech.internal",
            service_account=None,
            event_name="iam.serviceAccounts.list",
            event_source="iam.googleapis.com",
            source_ip="10.240.1.15",  # Internal corporate VPN IP
            is_suspicious=False,
            details_json=json.dumps({"filter": "status=active"}),
            timestamp=self.now - timedelta(hours=5)
        )
        db.add_all([iam_event_1, iam_event_2])
        db.flush()

    def _generate_documents(self, db: Session, services: dict):
        pay_srv = services["payments-service"]
        auth_srv = services["auth-service"]
        
        doc_defs = [
            (
                "Runbook: Payments Service Degradation & Rollback Procedures",
                DocumentCategory.RUNBOOK,
                pay_srv.id,
                """# Payments Service Emergency Response Runbook
## Symptoms
- 5xx HTTP response error rate > 5% on `/api/v1/charge` or `/api/v1/refund`.
- High database lock contention or p99 latency > 2000ms.

## Immediate Rollback Procedure
1. Check recent deployments using `get_recent_deployments(service="payments-service")`.
2. If a release occurred within 3 hours, initiate an immediate rollback to the previous stable release.
3. Target version: Confirm rollback target `v2.4.1`.
4. Command / Action: `ROLLBACK` target `payments-service` to version `v2.4.1`.
5. Post-rollback verification: Observe error rate dropping below 0.5% within 3 minutes and DB query latency normalizing under 25ms.
"""
            ),
            (
                "Postmortem: 2025 Database Row-Lock Contention Outage",
                DocumentCategory.POSTMORTEM,
                pay_srv.id,
                """# Postmortem: Database Lock Saturation Incident (P0)
## Root Cause
A code deployment introduced table row locking during high-frequency balance reads, leading to deadlocks across payment worker pools.
## Remediation
Rollback to previous release removed locking hints and restored non-blocking read replicas.
"""
            ),
            (
                "Security Policy: Service Account Least Privilege & Key Rotation",
                DocumentCategory.POLICY,
                auth_srv.id,
                """# NexaTech IAM Security Policy: Service Accounts
## Automated Escalation Detection
Any programmatic service account assuming Organization Admin or Project Owner roles from outside the VPC subnet (10.240.0.0/16) constitutes an immediate P1 security compromise.
## Incident Protocol
1. Revoke all active OAuth sessions immediately.
2. Rotate private key secrets and service account tokens.
3. Lock down IAM binding until forensic audit is completed.
"""
            ),
            (
                "Troubleshooting Guide: Container Dependency Vulnerabilities",
                DocumentCategory.RUNBOOK,
                auth_srv.id,
                """# Runbook: Urgent Patching of CVSS > 8.0 Vulnerabilities
## Verification
1. Inspect runtime dependency tree and external network interface.
2. If service is Internet-facing (e.g. auth-service), treat CVSS >= 8.5 as P1.
3. Action: Apply verified vendor patch and trigger rolling restart.
"""
            )
        ]

        for title, category, service_id, content in doc_defs:
            doc = Document(
                title=title,
                category=category,
                service_id=service_id,
                content=content.strip(),
                metadata_json=json.dumps({"author": "Core Platform Engineering", "version": "2026.1"})
            )
            db.add(doc)
            db.flush()

            # Split into chunks
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            for idx, p in enumerate(paragraphs):
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    content=p,
                    embedding_json=None  # will be populated by RAG pipeline
                )
                db.add(chunk)
        db.flush()

    def _generate_incidents(self, db: Session, services: dict, users: list, deployments: dict):
        pay_srv = services["payments-service"]
        lead_eng = users[1]
        
        # Scenario A Incident: INC-4091 (Payments post-deploy outage)
        inc_pay = Incident(
            incident_number="INC-4091",
            title="Payments Service experiencing elevated 5xx error rate (18.5%) post v2.4.2 deployment",
            description="Automated synthetic checkout monitor reported sustained failure rate > 15% immediately following deployment of PR #412.",
            service_id=pay_srv.id,
            severity=IncidentSeverity.P0,
            status=IncidentStatus.TRIGGERED,
            triggered_at=self.now - timedelta(hours=2, minutes=30),
            assigned_to_user_id=lead_eng.id
        )
        db.add(inc_pay)
        db.flush()

        # Timelines for INC-4091
        t1 = IncidentTimeline(
            incident_id=inc_pay.id,
            timestamp=self.now - timedelta(hours=2, minutes=45),
            title="Deployment Completed",
            description="payments-service release v2.4.2 deployed to production by lead.engineer@nexatech.internal",
            entry_type="SYSTEM_EVENT"
        )
        t2 = IncidentTimeline(
            incident_id=inc_pay.id,
            timestamp=self.now - timedelta(hours=2, minutes=30),
            title="Alert Fired: P0 ErrorRateSpike",
            description="5xx error rate crossed critical threshold (18.5% > 5.0%) on /api/v1/charge",
            entry_type="ALERT"
        )
        t3 = IncidentTimeline(
            incident_id=inc_pay.id,
            timestamp=self.now - timedelta(hours=2, minutes=20),
            title="Investigation Initiated",
            description="AI Operations Agent dispatched to analyze metrics, logs, PR diffs, and runbooks",
            entry_type="INVESTIGATION_NOTE"
        )
        db.add_all([t1, t2, t3])

        # Scenario D Incident: INC-3982 (Order Processing Canary Memory Leak)
        order_srv = services["order-processing"]
        inc_order = Incident(
            incident_number="INC-3982",
            title="Order-Processing Canary memory saturation and connection pool latency",
            description="Canary deployment v3.1.0-rc1 approaching OOM threshold (92% memory utilization).",
            service_id=order_srv.id,
            severity=IncidentSeverity.P2,
            status=IncidentStatus.INVESTIGATING,
            triggered_at=self.now - timedelta(hours=1),
            assigned_to_user_id=lead_eng.id
        )
        db.add(inc_order)
        db.flush()

        t_order = IncidentTimeline(
            incident_id=inc_order.id,
            timestamp=self.now - timedelta(hours=1),
            title="Canary Health Alert",
            description="Canary pod memory exceeded 85% safety boundary",
            entry_type="ALERT"
        )
        db.add(t_order)
        db.flush()
