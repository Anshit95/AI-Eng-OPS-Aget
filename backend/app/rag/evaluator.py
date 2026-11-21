import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.rag.retriever import search_knowledge
from backend.app.models.evaluation import EvaluationRun

RAG_BENCHMARK_QUERIES = [
    {
        "query": "payments service rollback procedure",
        "expected_doc_title": "Payments Service Degradation & Rollback Procedures",
        "expected_keywords": ["rollback", "v2.4.1", "charge", "5xx"],
        "scenario": "SCENARIO_A"
    },
    {
        "query": "database lock saturation row locking deadlock postmortem",
        "expected_doc_title": "2025 Database Row-Lock Contention Outage",
        "expected_keywords": ["lock", "deadlock", "rollback"],
        "scenario": "SCENARIO_A"
    },
    {
        "query": "service account privilege escalation organization admin rotation",
        "expected_doc_title": "Security Policy: Service Account Least Privilege & Key Rotation",
        "expected_keywords": ["rotation", "session", "compromise"],
        "scenario": "SCENARIO_C"
    },
    {
        "query": "container dependency CVE vulnerability patching",
        "expected_doc_title": "Troubleshooting Guide: Container Dependency Vulnerabilities",
        "expected_keywords": ["patch", "cvss", "vulnerability"],
        "scenario": "SCENARIO_B"
    }
]

def evaluate_rag_retrieval(db: Session) -> Dict[str, Any]:
    """Run reproducible RAG retrieval benchmark across operational runbooks."""
    hits = 0
    total = len(RAG_BENCHMARK_QUERIES)
    results = []

    for b in RAG_BENCHMARK_QUERIES:
        retrieved = search_knowledge(db, b["query"], limit=3)
        found_expected_doc = any(b["expected_doc_title"] in r["document_title"] for r in retrieved)
        
        # Check keyword groundedness
        combined_text = " ".join(r["content"].lower() for r in retrieved)
        keyword_hits = sum(1 for kw in b["expected_keywords"] if kw.lower() in combined_text)
        keyword_score = keyword_hits / max(1, len(b["expected_keywords"]))

        passed = found_expected_doc and keyword_score >= 0.5
        if passed:
            hits += 1

        results.append({
            "query": b["query"],
            "expected_doc": b["expected_doc_title"],
            "found_expected_doc": found_expected_doc,
            "keyword_groundedness": round(keyword_score, 2),
            "top_retrieved_title": retrieved[0]["document_title"] if retrieved else None,
            "top_similarity": retrieved[0]["similarity_score"] if retrieved else 0.0,
            "passed": passed
        })

    accuracy = hits / max(1, total)

    eval_record = EvaluationRun(
        suite_name="RAG_RETRIEVAL",
        ground_truth_scenario="ALL_SCENARIOS",
        passed=(accuracy >= 0.75),
        precision=accuracy,
        recall=accuracy,
        f1=accuracy,
        accuracy=accuracy,
        details_json=json.dumps({"queries": results, "total": total, "passed_count": hits})
    )
    db.add(eval_record)
    db.commit()

    return {
        "suite": "RAG_RETRIEVAL",
        "total_queries": total,
        "passed_queries": hits,
        "accuracy": round(accuracy, 3),
        "results": results
    }
