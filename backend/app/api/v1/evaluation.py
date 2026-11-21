import json
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.evaluation import EvaluationRun
from backend.app.api.deps import get_current_user, require_role
from backend.app.models.user import User, UserRole
from backend.app.rag.evaluator import evaluate_rag_retrieval
from backend.app.agent.orchestrator import InvestigationOrchestrator
from backend.app.models.incident import Incident

router = APIRouter()
GROUND_TRUTH_PATH = Path(__file__).resolve().parent.parent.parent.parent / "eval" / "ground_truth.json"

@router.get("/runs")
def list_evaluation_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(limit).all()
    results = []
    for r in runs:
        results.append({
            "id": r.id,
            "suite_name": r.suite_name,
            "ground_truth_scenario": r.ground_truth_scenario,
            "passed": r.passed,
            "precision": r.precision,
            "recall": r.recall,
            "f1": r.f1,
            "accuracy": r.accuracy,
            "details": json.loads(r.details_json or "{}"),
            "created_at": r.created_at.isoformat()
        })
    return results

@router.post("/run-suite")
def run_evaluation_suite(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER, UserRole.ADMINISTRATOR]))
):
    suite_results = {}
    
    # 1. RAG Benchmark
    rag_eval = evaluate_rag_retrieval(db)
    suite_results["rag_retrieval"] = rag_eval

    # 2. Agent Scenario A Ground-Truth Benchmark
    ground_truth = {}
    if GROUND_TRUTH_PATH.exists():
        with open(GROUND_TRUTH_PATH, "r") as f:
            ground_truth = json.load(f)

    scenario_a = ground_truth.get("SCENARIO_A", {})
    inc_a = db.query(Incident).filter(Incident.incident_number == scenario_a.get("incident_number", "INC-4091")).first()
    
    scenario_a_passed = False
    details_a = {}
    if inc_a:
        orchestrator = InvestigationOrchestrator(db, user_role=current_user.role.value)
        inv_res = orchestrator.run_investigation(inc_a.id)
        
        # Check if root cause keywords and recommended action match ground truth
        hyp_text = " ".join(h.get("title", "") + " " + h.get("description", "") for h in inv_res.get("root_cause_hypotheses", [])).lower()
        keyword_hits = sum(1 for kw in scenario_a.get("expected_root_cause_keywords", []) if kw.lower() in hyp_text)
        action_match = any(r.get("action_type") == scenario_a.get("expected_remediation_action") for r in inv_res.get("recommendations", []))
        
        scenario_a_passed = (keyword_hits >= 2 and action_match)
        details_a = {
            "incident_number": inc_a.incident_number,
            "keyword_hits": keyword_hits,
            "action_match": action_match,
            "confidence": inv_res.get("confidence_score"),
            "passed": scenario_a_passed
        }

        db.add(EvaluationRun(
            suite_name="AGENT_SCENARIO_A",
            ground_truth_scenario="SCENARIO_A",
            passed=scenario_a_passed,
            precision=1.0 if scenario_a_passed else 0.0,
            recall=1.0 if scenario_a_passed else 0.0,
            f1=1.0 if scenario_a_passed else 0.0,
            accuracy=1.0 if scenario_a_passed else 0.0,
            details_json=json.dumps(details_a)
        ))
        db.commit()

    suite_results["scenario_a_benchmark"] = details_a

    return {
        "status": "COMPLETED",
        "timestamp": json.dumps(None),
        "results": suite_results
    }
