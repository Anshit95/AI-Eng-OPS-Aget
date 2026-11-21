from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from backend.app.core.database import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    suite_name = Column(String(100), nullable=False, index=True)  # ML_ANOMALY, ML_SEVERITY, ML_DEPLOY_RISK, RAG_RETRIEVAL, AGENT_WORKFLOW
    ground_truth_scenario = Column(String(100), nullable=False, index=True)  # SCENARIO_A, SCENARIO_B, SCENARIO_C, SCENARIO_D, SCENARIO_E
    passed = Column(Boolean, default=False, nullable=False)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1 = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
