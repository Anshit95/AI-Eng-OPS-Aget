import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.service import Service
from backend.app.models.incident import Incident

client = TestClient(app)

def get_auth_token(email: str, password: str = "NexaTech2026!Secure") -> str:
    res = client.post("/api/v1/auth/login/json", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]

def test_health_endpoints():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    res_v1 = client.get("/api/v1/health/health")
    assert res_v1.status_code == 200
    assert res_v1.json()["database"] == "ok"

def test_auth_success_and_failure():
    # Valid login
    res = client.post("/api/v1/auth/login/json", json={
        "email": "admin@nexatech.internal",
        "password": "NexaTech2026!Secure"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "Administrator"

    # Invalid login
    res_bad = client.post("/api/v1/auth/login/json", json={
        "email": "admin@nexatech.internal",
        "password": "WrongPassword!"
    })
    assert res_bad.status_code == 401

def test_rbac_permissions():
    viewer_token = get_auth_token("ops.viewer@nexatech.internal")
    engineer_token = get_auth_token("lead.engineer@nexatech.internal")
    admin_token = get_auth_token("admin@nexatech.internal")

    headers_viewer = {"Authorization": f"Bearer {viewer_token}"}
    headers_eng = {"Authorization": f"Bearer {engineer_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 1. Viewer can read dashboard overview
    res_dash = client.get("/api/v1/dashboard/overview", headers=headers_viewer)
    assert res_dash.status_code == 200

    # 2. Viewer cannot create incident (Requires Engineer+) -> Expect 403
    res_forbidden = client.post("/api/v1/incidents/", headers=headers_viewer, json={
        "title": "Unauthorized Incident Creation",
        "service_id": 1,
        "severity": "P2"
    })
    assert res_forbidden.status_code == 403

    # 3. Engineer can propose an action
    res_propose = client.post("/api/v1/actions/", headers=headers_eng, json={
        "action_type": "ROLLBACK",
        "target_resource": "payments-service",
        "parameters": {"target_version": "v2.4.1"}
    })
    assert res_propose.status_code == 200
    action_id = res_propose.json()["id"]
    assert res_propose.json()["status"] == "PENDING_APPROVAL"

    # 4. Engineer cannot approve actions (Requires Administrator) -> Expect 403
    res_eng_approve = client.post(f"/api/v1/actions/{action_id}/approve", headers=headers_eng, json={"approved": True})
    assert res_eng_approve.status_code == 403

    # 5. Administrator can approve action
    res_admin_approve = client.post(f"/api/v1/actions/{action_id}/approve", headers=headers_admin, json={"approved": True})
    assert res_admin_approve.status_code == 200
    assert res_admin_approve.json()["status"] == "APPROVED"

def test_ml_inference_endpoints():
    token = get_auth_token("admin@nexatech.internal")
    headers = {"Authorization": f"Bearer {token}"}

    # A. Anomaly Detection
    res_anom = client.post("/api/v1/ml/anomaly/detect", headers=headers, json={
        "service_slug": "payments-service",
        "error_rate": 18.5,
        "latency_p95": 2800.0,
        "latency_p99": 3900.0,
        "cpu_usage": 88.0,
        "memory_usage": 72.0,
        "db_latency": 1100.0
    })
    assert res_anom.status_code == 200
    anom_json = res_anom.json()
    assert anom_json["is_anomaly"] == True
    assert anom_json["anomaly_score"] > 0.60

    # B. Severity Prediction
    res_sev = client.post("/api/v1/ml/severity/predict", headers=headers, json={
        "service_tier": "Tier-1",
        "error_rate": 18.5,
        "impacted_users_pct": 35.0,
        "has_security_flag": False,
        "recent_deploy_minutes": 25
    })
    assert res_sev.status_code == 200
    assert res_sev.json()["predicted_severity"] in ["P0", "P1"]

    # C. Deployment Risk Estimation (pre-deployment features)
    res_risk = client.post("/api/v1/ml/deployment-risk/predict", headers=headers, json={
        "service_tier": "Tier-1",
        "lines_added": 220,
        "lines_deleted": 15,
        "files_changed": 8,
        "has_migrations": True,
        "author_prior_deployments": 3,
        "is_friday_or_weekend": True
    })
    assert res_risk.status_code == 200
    assert res_risk.json()["risk_level"] in ["HIGH", "CRITICAL"]

def test_rag_knowledge_search():
    token = get_auth_token("admin@nexatech.internal")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/knowledge/search", headers=headers, json={
        "query": "payments service emergency rollback procedures",
        "limit": 3
    })
    assert res.status_code == 200
    data = res.json()
    assert data["retrieval_count"] > 0
    found_rollback_guidance = any("rollback" in c["content"].lower() or "v2.4.1" in c["content"] for c in data["chunks"])
    assert found_rollback_guidance

def test_agent_investigation_and_remediation_lifecycle():
    token = get_auth_token("admin@nexatech.internal")
    headers = {"Authorization": f"Bearer {token}"}

    # Find the payments incident
    db = SessionLocal()
    inc = db.query(Incident).filter(Incident.incident_number == "INC-4091").first()
    db.close()
    assert inc is not None

    # Run agent investigation
    res_inv = client.post("/api/v1/agent/investigate", headers=headers, json={"incident_id": inc.id})
    assert res_inv.status_code == 200
    inv_data = res_inv.json()
    assert inv_data["status"] == "COMPLETED"
    assert len(inv_data["root_cause_hypotheses"]) > 0
    assert inv_data["confidence_score"] >= 0.80

    # Verify recommendations contain ROLLBACK
    recs = inv_data["recommendations"]
    assert any(r["action_type"] == "ROLLBACK" for r in recs)

    # Propose the rollback action
    res_prop = client.post("/api/v1/actions/", headers=headers, json={
        "incident_id": inc.id,
        "investigation_id": inv_data["investigation_id"],
        "action_type": "ROLLBACK",
        "target_resource": "payments-service",
        "parameters": {"target_version": "v2.4.1"}
    })
    assert res_prop.status_code == 200
    action_id = res_prop.json()["id"]

    # Approve action
    res_app = client.post(f"/api/v1/actions/{action_id}/approve", headers=headers, json={"approved": True})
    assert res_app.status_code == 200

    # Execute action and verify post-action state
    res_exec = client.post(f"/api/v1/actions/{action_id}/execute", headers=headers)
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    assert exec_data["status"] == "VERIFIED"
    assert exec_data["verification_result"]["verified"] == True
    assert exec_data["verification_result"]["health_check_status"] == "HEALTHY"

    # Verify the database service record was updated to target version v2.4.1
    db = SessionLocal()
    srv = db.query(Service).filter(Service.slug == "payments-service").first()
    assert srv.active_version == "v2.4.1"
    assert srv.status.value == "HEALTHY"
    db.close()
