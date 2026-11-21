import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class InvestigationStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ActionType(str, enum.Enum):
    ROLLBACK = "ROLLBACK"
    RESTART_SERVICE = "RESTART_SERVICE"
    ROTATE_CREDENTIALS = "ROTATE_CREDENTIALS"
    ISOLATE_POD = "ISOLATE_POD"
    APPLY_HOTFIX = "APPLY_HOTFIX"

class ActionStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    status = Column(Enum(InvestigationStatus), default=InvestigationStatus.IN_PROGRESS, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    root_cause_hypotheses_json = Column(Text, nullable=True)
    evidence_citations_json = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    token_usage_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    incident = relationship("Incident", back_populates="investigations")
    actions = relationship("ActionRequest", back_populates="investigation")

class ActionRequest(Base):
    __tablename__ = "action_requests"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True, index=True)
    action_type = Column(Enum(ActionType), nullable=False)
    target_resource = Column(String(200), nullable=False)
    parameters_json = Column(Text, nullable=True)
    status = Column(Enum(ActionStatus), default=ActionStatus.PROPOSED, nullable=False, index=True)
    requested_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    execution_result_json = Column(Text, nullable=True)
    verification_result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="actions")
    incident = relationship("Incident", back_populates="actions")
    requested_by = relationship("User", foreign_keys=[requested_by_user_id], back_populates="actions_requested")
    approved_by = relationship("User", foreign_keys=[approved_by_user_id], back_populates="actions_approved")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True)
    details_json = Column(Text, nullable=True)
    ip_address = Column(String(45), default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
