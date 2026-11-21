import json
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.ml.anomaly_detector import anomaly_detector
from backend.app.ml.severity_predictor import severity_predictor
from backend.app.ml.deployment_risk import deployment_risk_estimator
from backend.app.schemas.ml import (
    AnomalyInferenceRequest, AnomalyInferenceResponse,
    SeverityPredictRequest, SeverityPredictResponse,
    DeploymentRiskRequest, DeploymentRiskResponse
)
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()
REPORT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "models" / "eval_report.json"

@router.get("/info")
def get_ml_models_info(current_user: User = Depends(get_current_user)):
    report = {}
    if REPORT_PATH.exists():
        try:
            with open(REPORT_PATH, "r") as f:
                report = json.load(f)
        except Exception:
            pass

    return {
        "models": {
            "anomaly_detector": {
                "name": "Isolation Forest Anomaly Detector",
                "status": "LOADED" if anomaly_detector.model is not None else "UNINITIALIZED",
                "features": ["error_rate", "latency_p95", "latency_p99", "cpu_usage", "memory_usage", "db_latency"],
                "metrics": report.get("anomaly_detection", {})
            },
            "severity_predictor": {
                "name": "Random Forest Incident Severity Classifier",
                "status": "LOADED" if severity_predictor.model is not None else "UNINITIALIZED",
                "features": ["tier_level", "error_rate", "impacted_users_pct", "has_security_flag", "recent_deploy_minutes"],
                "classes": ["P0", "P1", "P2", "P3"],
                "metrics": report.get("severity_prediction", {})
            },
            "deployment_risk": {
                "name": "Gradient Boosting Pre-Deployment Risk Estimator",
                "status": "LOADED" if deployment_risk_estimator.model is not None else "UNINITIALIZED",
                "features": ["tier_level", "lines_added", "lines_deleted", "files_changed", "has_migrations", "author_prior_deployments", "is_friday_or_weekend"],
                "leakage_prevention": "Strict pre-deployment feature boundary",
                "metrics": report.get("deployment_risk", {})
            }
        }
    }

@router.post("/anomaly/detect", response_model=AnomalyInferenceResponse)
def detect_anomaly(
    payload: AnomalyInferenceRequest,
    current_user: User = Depends(get_current_user)
):
    res = anomaly_detector.detect(payload.model_dump())
    return AnomalyInferenceResponse(
        service_slug=payload.service_slug,
        is_anomaly=res["is_anomaly"],
        anomaly_score=res["anomaly_score"],
        contributing_features=res["contributing_features"],
        baseline_comparison=res["baseline_comparison"],
        explanation=res["explanation"]
    )

@router.post("/severity/predict", response_model=SeverityPredictResponse)
def predict_severity(
    payload: SeverityPredictRequest,
    current_user: User = Depends(get_current_user)
):
    res = severity_predictor.predict(payload.model_dump())
    return SeverityPredictResponse(
        predicted_severity=res["predicted_severity"],
        confidence=res["confidence"],
        probabilities=res["probabilities"],
        top_factors=res["top_factors"]
    )

@router.post("/deployment-risk/predict", response_model=DeploymentRiskResponse)
def predict_deployment_risk(
    payload: DeploymentRiskRequest,
    current_user: User = Depends(get_current_user)
):
    res = deployment_risk_estimator.estimate(payload.model_dump())
    return DeploymentRiskResponse(
        risk_score=res["risk_score"],
        risk_level=res["risk_level"],
        recommended_strategy=res["recommended_strategy"],
        top_risk_factors=res["top_risk_factors"]
    )
