from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SecurityFindingResponse(BaseModel):
    id: int
    service_id: int
    service_name: Optional[str] = None
    cve_id: Optional[str]
    title: str
    description: Optional[str]
    severity: str
    cvss_score: float
    package_name: Optional[str]
    affected_version: Optional[str]
    fixed_version: Optional[str]
    attack_vector: str
    is_exploitable: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IAMEventResponse(BaseModel):
    id: int
    user_email: Optional[str]
    service_account: Optional[str]
    event_name: str
    event_source: str
    source_ip: str
    is_suspicious: bool
    details_json: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
