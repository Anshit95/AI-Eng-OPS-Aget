import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class IncidentSeverity(str, enum.Enum):
    P0 = "P0"  # Critical outage / complete loss of core service
    P1 = "P1"  # Major degradation / significant revenue or security impact
    P2 = "P2"  # Moderate impact / redundancy compromised
    P3 = "P3"  # Minor / low impact issue

class IncidentStatus(str, enum.Enum):
    TRIGGERED = "TRIGGERED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATED = "MITIGATED"
    RESOLVED = "RESOLVED"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.P2, nullable=False, index=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.TRIGGERED, nullable=False, index=True)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    root_cause = Column(Text, nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    service = relationship("Service", back_populates="incidents")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id])
    timeline = relationship("IncidentTimeline", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentTimeline.timestamp")
    investigations = relationship("Investigation", back_populates="incident", cascade="all, delete-orphan")
    actions = relationship("ActionRequest", back_populates="incident")

class IncidentTimeline(Base):
    __tablename__ = "incident_timelines"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    entry_type = Column(String(50), default="ALERT")  # ALERT, SYSTEM_EVENT, INVESTIGATION_NOTE, ACTION_EXECUTED

    incident = relationship("Incident", back_populates="timeline")
