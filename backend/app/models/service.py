import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ServiceTier(str, enum.Enum):
    TIER_1 = "Tier-1"
    TIER_2 = "Tier-2"
    TIER_3 = "Tier-3"

class ServiceStatus(str, enum.Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"

class DeploymentEnvironment(str, enum.Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    CANARY = "canary"

class DeploymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    tier = Column(Enum(ServiceTier), default=ServiceTier.TIER_2, nullable=False)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.HEALTHY, nullable=False)
    owner_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    repo_url = Column(String(255), nullable=True)
    language = Column(String(50), default="Python")
    framework = Column(String(50), default="FastAPI")
    active_version = Column(String(50), default="v1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner_team = relationship("Team", back_populates="services")
    repositories = relationship("Repository", back_populates="service", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="service", cascade="all, delete-orphan")
    metrics = relationship("MetricObservation", back_populates="service", cascade="all, delete-orphan")
    logs = relationship("LogEntry", back_populates="service", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="service")
    security_findings = relationship("SecurityFinding", back_populates="service", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="service")

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    default_branch = Column(String(50), default="main")
    visibility = Column(String(20), default="internal")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    service = relationship("Service", back_populates="repositories")
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")

class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    commit_sha = Column(String(40), unique=True, index=True, nullable=False)
    author_email = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    files_changed_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    repository = relationship("Repository", back_populates="commits")

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author_email = Column(String(120), nullable=False)
    status = Column(String(20), default="MERGED")
    head_sha = Column(String(40), nullable=False)
    base_sha = Column(String(40), default="main")
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    files_changed_count = Column(Integer, default=1)
    has_migrations = Column(Boolean, default=False)
    merged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    repository = relationship("Repository", back_populates="pull_requests")
    deployments = relationship("Deployment", back_populates="pull_request")

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=True)
    commit_sha = Column(String(40), nullable=False)
    version = Column(String(50), nullable=False)
    environment = Column(Enum(DeploymentEnvironment), default=DeploymentEnvironment.PRODUCTION, nullable=False)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.SUCCESS, nullable=False)
    deployed_by = Column(String(120), nullable=False)
    risk_score = Column(Float, default=0.1)
    rollback_target_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    service = relationship("Service", back_populates="deployments")
    pull_request = relationship("PullRequest", back_populates="deployments")
