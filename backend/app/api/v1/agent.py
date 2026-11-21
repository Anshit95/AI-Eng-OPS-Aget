from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.agent.orchestrator import InvestigationOrchestrator
from backend.app.api.deps import get_current_user, require_role, record_audit
from backend.app.models.user import User, UserRole

router = APIRouter()

class AgentInvestigateRequest(BaseModel):
    incident_id: int

@router.get("/status")
def get_agent_status(current_user: User = Depends(get_current_user)):
    return {
        "status": "ONLINE",
        "orchestrator": "Google ADK & Gemini Investigation Engine",
        "model": settings.GEMINI_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY),
        "execution_mode": "LIVE_GENAI" if settings.GEMINI_API_KEY else "DETERMINISTIC_HYBRID_ENGINE",
        "safety_controls": {
            "untrusted_data_isolation": True,
            "least_privilege_rbac": True,
            "human_in_the_loop_approvals": True,
            "post_action_independent_verification": True
        }
    }

@router.post("/investigate")
def run_agent_investigation(
    payload: AgentInvestigateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER, UserRole.SECURITY_ANALYST, UserRole.ADMINISTRATOR]))
):
    orchestrator = InvestigationOrchestrator(db, user_role=current_user.role.value)
    result = orchestrator.run_investigation(payload.incident_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    record_audit(
        db, current_user, "AGENT_INVESTIGATION_RUN", "Incident", str(payload.incident_id),
        {"investigation_id": result.get("investigation_id")}
    )
    return result
