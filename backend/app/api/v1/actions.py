import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.investigation import ActionRequest, ActionType, ActionStatus
from backend.app.models.user import User, UserRole
from backend.app.schemas.investigation import ActionResponse, ActionRequestCreate, ActionApprovalRequest
from backend.app.api.deps import get_current_user, require_role, record_audit
from backend.app.simulator.adapters import NexaRemediationAdapter

router = APIRouter()

@router.get("/", response_model=List[ActionResponse])
def list_actions(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ActionRequest)
    if status_filter:
        query = query.filter(ActionRequest.status == status_filter.upper())

    actions = query.order_by(ActionRequest.created_at.desc()).all()
    results = []
    for a in actions:
        res = ActionResponse(
            id=a.id,
            investigation_id=a.investigation_id,
            incident_id=a.incident_id,
            action_type=a.action_type.value,
            target_resource=a.target_resource,
            status=a.status.value,
            parameters=json.loads(a.parameters_json or "{}"),
            requested_by_email=a.requested_by.email if a.requested_by else "system",
            approved_by_email=a.approved_by.email if a.approved_by else None,
            execution_result=json.loads(a.execution_result_json) if a.execution_result_json else None,
            verification_result=json.loads(a.verification_result_json) if a.verification_result_json else None,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        results.append(res)
    return results

@router.post("/", response_model=ActionResponse)
def propose_action(
    payload: ActionRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER, UserRole.SECURITY_ANALYST, UserRole.ADMINISTRATOR]))
):
    try:
        act_type = ActionType(payload.action_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action_type: {payload.action_type}")

    action = ActionRequest(
        investigation_id=payload.investigation_id,
        incident_id=payload.incident_id,
        action_type=act_type,
        target_resource=payload.target_resource,
        parameters_json=json.dumps(payload.parameters),
        status=ActionStatus.PENDING_APPROVAL,
        requested_by_user_id=current_user.id
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    record_audit(
        db, current_user, "ACTION_PROPOSED", "ActionRequest", str(action.id),
        {"type": act_type.value, "target": payload.target_resource, "params": payload.parameters}
    )

    return ActionResponse(
        id=action.id,
        investigation_id=action.investigation_id,
        incident_id=action.incident_id,
        action_type=action.action_type.value,
        target_resource=action.target_resource,
        status=action.status.value,
        parameters=payload.parameters,
        requested_by_email=current_user.email,
        approved_by_email=None,
        execution_result=None,
        verification_result=None,
        created_at=action.created_at,
        updated_at=action.updated_at
    )

@router.post("/{action_id}/approve", response_model=ActionResponse)
def review_action(
    action_id: int,
    payload: ActionApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMINISTRATOR]))
):
    action = db.query(ActionRequest).filter(ActionRequest.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action request not found")

    if action.status != ActionStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail=f"Action is not pending approval (current status: {action.status.value})")

    action.approved_by_user_id = current_user.id
    action.updated_at = datetime.utcnow()

    if payload.approved:
        action.status = ActionStatus.APPROVED
        record_audit(db, current_user, "ACTION_APPROVED", "ActionRequest", str(action.id))
    else:
        action.status = ActionStatus.REJECTED
        exec_meta = {"rejection_reason": payload.rejection_reason or "Rejected by administrator"}
        action.execution_result_json = json.dumps(exec_meta)
        record_audit(db, current_user, "ACTION_REJECTED", "ActionRequest", str(action.id), exec_meta)

    db.commit()
    db.refresh(action)

    return ActionResponse(
        id=action.id,
        investigation_id=action.investigation_id,
        incident_id=action.incident_id,
        action_type=action.action_type.value,
        target_resource=action.target_resource,
        status=action.status.value,
        parameters=json.loads(action.parameters_json or "{}"),
        requested_by_email=action.requested_by.email if action.requested_by else "system",
        approved_by_email=current_user.email,
        execution_result=json.loads(action.execution_result_json) if action.execution_result_json else None,
        verification_result=None,
        created_at=action.created_at,
        updated_at=action.updated_at
    )

@router.post("/{action_id}/execute", response_model=ActionResponse)
def execute_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMINISTRATOR, UserRole.ENGINEER]))
):
    action = db.query(ActionRequest).filter(ActionRequest.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action request not found")

    if action.status != ActionStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute action. Status must be APPROVED, but current status is {action.status.value}"
        )

    action.status = ActionStatus.EXECUTING
    db.commit()

    adapter = NexaRemediationAdapter(db)
    params = json.loads(action.parameters_json or "{}")
    success = False
    exec_res = {}
    verif_res = {}

    try:
        if action.action_type == ActionType.ROLLBACK:
            target_version = params.get("target_version")
            if not target_version:
                raise ValueError("Missing 'target_version' parameter for rollback")
            success, exec_res, verif_res = adapter.execute_rollback(action.target_resource, target_version)

        elif action.action_type == ActionType.ROTATE_CREDENTIALS:
            success, exec_res, verif_res = adapter.execute_credential_rotation(action.target_resource)

        elif action.action_type == ActionType.APPLY_HOTFIX:
            cve_id = params.get("cve_id", "CVE-2024-21626")
            fixed_version = params.get("fixed_version", "v1.1.12")
            success, exec_res, verif_res = adapter.execute_hotfix_patch(action.target_resource, cve_id, fixed_version)

        else:
            exec_res = {"status": "SUCCESS", "message": f"Action {action.action_type.value} dispatched."}
            verif_res = {"verified": True, "health": "HEALTHY"}
            success = True

        action.status = ActionStatus.VERIFIED if success else ActionStatus.FAILED
        action.execution_result_json = json.dumps(exec_res)
        action.verification_result_json = json.dumps(verif_res)
        action.updated_at = datetime.utcnow()
        db.commit()

        record_audit(
            db, current_user, "ACTION_EXECUTED", "ActionRequest", str(action.id),
            {"status": action.status.value, "verification": verif_res}
        )

    except Exception as e:
        action.status = ActionStatus.FAILED
        action.execution_result_json = json.dumps({"error": str(e)})
        action.updated_at = datetime.utcnow()
        db.commit()
        record_audit(db, current_user, "ACTION_EXECUTION_FAILED", "ActionRequest", str(action.id), {"error": str(e)})

    return ActionResponse(
        id=action.id,
        investigation_id=action.investigation_id,
        incident_id=action.incident_id,
        action_type=action.action_type.value,
        target_resource=action.target_resource,
        status=action.status.value,
        parameters=params,
        requested_by_email=action.requested_by.email if action.requested_by else "system",
        approved_by_email=action.approved_by.email if action.approved_by else None,
        execution_result=exec_res,
        verification_result=verif_res,
        created_at=action.created_at,
        updated_at=action.updated_at
    )
