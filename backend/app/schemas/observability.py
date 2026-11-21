from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MetricObservationResponse(BaseModel):
    id: int
    service_id: int
    timestamp: datetime
    error_rate: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    request_count: int
    cpu_usage: float
    memory_usage: float
    db_latency: float

    model_config = ConfigDict(from_attributes=True)

class LogEntryResponse(BaseModel):
    id: int
    service_id: int
    timestamp: datetime
    level: str
    message: str
    trace_id: Optional[str]
    span_id: Optional[str]
    source: str
    metadata_json: Optional[str]

    model_config = ConfigDict(from_attributes=True)
