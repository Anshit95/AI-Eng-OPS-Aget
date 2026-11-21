from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class MetricObservation(Base):
    __tablename__ = "metric_observations"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    error_rate = Column(Float, default=0.0)         # percentage 0.0 - 100.0
    latency_p50 = Column(Float, default=50.0)       # ms
    latency_p95 = Column(Float, default=120.0)      # ms
    latency_p99 = Column(Float, default=250.0)      # ms
    request_count = Column(Integer, default=100)    # req/sec
    cpu_usage = Column(Float, default=25.0)         # percentage 0.0 - 100.0
    memory_usage = Column(Float, default=45.0)      # percentage 0.0 - 100.0
    db_latency = Column(Float, default=15.0)        # ms

    service = relationship("Service", back_populates="metrics")

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(String(20), default="INFO", index=True)  # INFO, WARN, ERROR, FATAL
    message = Column(Text, nullable=False)
    trace_id = Column(String(64), nullable=True, index=True)
    span_id = Column(String(64), nullable=True)
    source = Column(String(100), default="application")
    metadata_json = Column(Text, nullable=True)

    service = relationship("Service", back_populates="logs")
