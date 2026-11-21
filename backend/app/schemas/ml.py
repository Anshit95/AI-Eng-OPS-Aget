from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AnomalyInferenceRequest(BaseModel):
    service_slug: str
    error_rate: float
    latency_p95: float
    latency_p99: float
    cpu_usage: float
    memory_usage: float
    db_latency: float

class AnomalyInferenceResponse(BaseModel):
    service_slug: str
    is_anomaly: bool
    anomaly_score: float
    contributing_features: Dict[str, float]
    baseline_comparison: Dict[str, Any]
    explanation: str

class SeverityPredictRequest(BaseModel):
    service_tier: str  # Tier-1, Tier-2, Tier-3
    error_rate: float
    impacted_users_pct: float
    has_security_flag: bool
    recent_deploy_minutes: int

class SeverityPredictResponse(BaseModel):
    predicted_severity: str  # P0, P1, P2, P3
    confidence: float
    probabilities: Dict[str, float]
    top_factors: List[str]

class DeploymentRiskRequest(BaseModel):
    service_tier: str
    lines_added: int
    lines_deleted: int
    files_changed: int
    has_migrations: bool
    author_prior_deployments: int
    is_friday_or_weekend: bool

class DeploymentRiskResponse(BaseModel):
    risk_score: float
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    recommended_strategy: str  # DIRECT, CANARY, MANUAL_APPROVAL_REQUIRED
    top_risk_factors: List[str]

class DocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    service_id: Optional[int]
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RAGSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    service_id: Optional[int] = None
    limit: int = 4

class RAGSearchResponse(BaseModel):
    query: str
    chunks: List[Dict[str, Any]]
    retrieval_count: int
