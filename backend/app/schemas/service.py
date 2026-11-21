from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ServiceResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    tier: str
    status: str
    repo_url: Optional[str]
    language: str
    framework: str
    active_version: str
    owner_team_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DeploymentResponse(BaseModel):
    id: int
    service_id: int
    service_name: Optional[str] = None
    commit_sha: str
    version: str
    environment: str
    status: str
    deployed_by: str
    risk_score: float
    rollback_target_version: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PullRequestResponse(BaseModel):
    id: int
    pr_number: int
    title: str
    description: Optional[str]
    author_email: str
    status: str
    head_sha: str
    base_sha: str
    lines_added: int
    lines_deleted: int
    files_changed_count: int
    has_migrations: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
