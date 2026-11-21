from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class IncidentTimelineResponse(BaseModel):
    id: int
    timestamp: datetime
    title: str
    description: Optional[str]
    entry_type: str

    model_config = ConfigDict(from_attributes=True)

class IncidentResponse(BaseModel):
    id: int
    incident_number: str
    title: str
    description: Optional[str]
    service_id: int
    service_name: Optional[str] = None
    service_slug: Optional[str] = None
    severity: str
    status: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    root_cause: Optional[str] = None
    assigned_to_email: Optional[str] = None
    timeline: List[IncidentTimelineResponse] = []

    model_config = ConfigDict(from_attributes=True)

class IncidentCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    service_id: int
    severity: str = "P2"
