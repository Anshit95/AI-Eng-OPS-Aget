from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.service import Deployment, Service, PullRequest
from backend.app.schemas.service import DeploymentResponse, PullRequestResponse
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[DeploymentResponse])
def list_deployments(
    service_slug: Optional[str] = None,
    environment: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Deployment)
    if service_slug:
        query = query.join(Service).filter(Service.slug == service_slug)
    if environment:
        query = query.filter(Deployment.environment == environment)

    deployments = query.order_by(Deployment.created_at.desc()).limit(limit).all()
    results = []
    for d in deployments:
        res = DeploymentResponse.model_validate(d)
        res.service_name = d.service.name if d.service else None
        results.append(res)
    return results

@router.get("/pull-requests", response_model=List[PullRequestResponse])
def list_pull_requests(
    service_slug: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(PullRequest)
    if service_slug:
        query = query.join(PullRequest.repository).join(Service).filter(Service.slug == service_slug)
    prs = query.order_by(PullRequest.created_at.desc()).limit(limit).all()
    return prs
