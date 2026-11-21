from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class InvestigationResponse(BaseModel):
    id: int
    incident_id: int
    incident_number: Optional[str] = None
    service_name: Optional[str] = None
    status: str
    summary: Optional[str]
    root_cause_hypotheses: List[Dict[str, Any]] = []
    evidence_citations: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []
    confidence_score: float
    token_usage: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvestigationCreateRequest(BaseModel):
    incident_id: int
    enable_ml_analysis: bool = True
    enable_rag_search: bool = True

class ActionRequestCreate(BaseModel):
    incident_id: Optional[int] = None
    investigation_id: Optional[int] = None
    action_type: str  # ROLLBACK, RESTART_SERVICE, ROTATE_CREDENTIALS, ISOLATE_POD, APPLY_HOTFIX
    target_resource: str
    parameters: Dict[str, Any] = {}

class ActionApprovalRequest(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None

class ActionResponse(BaseModel):
    id: int
    investigation_id: Optional[int]
    incident_id: Optional[int]
    action_type: str
    target_resource: str
    status: str
    parameters: Dict[str, Any] = {}
    requested_by_email: str
    approved_by_email: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
