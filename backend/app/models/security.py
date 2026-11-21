import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class FindingSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class FindingStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"

class SecurityFinding(Base):
    __tablename__ = "security_findings"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    cve_id = Column(String(50), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(FindingSeverity), default=FindingSeverity.MEDIUM, nullable=False, index=True)
    cvss_score = Column(Float, default=5.0)
    package_name = Column(String(100), nullable=True)
    affected_version = Column(String(50), nullable=True)
    fixed_version = Column(String(50), nullable=True)
    attack_vector = Column(String(50), default="NETWORK")  # NETWORK, LOCAL, ADJACENT
    is_exploitable = Column(Boolean, default=False)
    status = Column(Enum(FindingStatus), default=FindingStatus.OPEN, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    service = relationship("Service", back_populates="security_findings")

class IAMEvent(Base):
    __tablename__ = "iam_events"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(120), nullable=True, index=True)
    service_account = Column(String(120), nullable=True, index=True)
    event_name = Column(String(100), nullable=False, index=True)
    event_source = Column(String(100), default="iam.googleapis.com")
    source_ip = Column(String(45), default="127.0.0.1")
    is_suspicious = Column(Boolean, default=False, index=True)
    details_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
