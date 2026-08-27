from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mode = Column(String, nullable=False) # 'demo' or 'evaluation'
    provider = Column(String, nullable=False, default="SYNTHETIC")
    status = Column(String, nullable=False, default="STARTED") # STARTED, PROCESSING, COMPLETED, FAILED
    
    # Run parameters
    size = Column(Integer)
    seed = Column(Integer)
    
    # Metrics
    records_processed = Column(Integer, default=0)
    scenario_count = Column(Integer, default=0)
    verified_match = Column(Integer, default=0)
    explainable_variance = Column(Integer, default=0)
    review = Column(Integer, default=0)
    unresolved = Column(Integer, default=0)
    duplicate_conflict = Column(Integer, default=0)
    
    elapsed_seconds = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matches = relationship("ReconciliationMatch", back_populates="run", cascade="all, delete-orphan")
    exceptions = relationship("ExceptionRecord", back_populates="run", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="run", cascade="all, delete-orphan")


class ReconciliationMatch(Base):
    __tablename__ = "reconciliation_matches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("reconciliation_runs.id"), nullable=False)
    
    scenario_id = Column(String)
    decision = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    
    order_id = Column(String)
    payment_id = Column(String)
    settlement_id = Column(String)
    bank_transaction_id = Column(String)
    
    variance_details = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    run = relationship("ReconciliationRun", back_populates="matches")


class ExceptionRecord(Base):
    __tablename__ = "exceptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("reconciliation_runs.id"), nullable=False)
    
    scenario_id = Column(String)
    exception_type = Column(String, nullable=False)
    decision = Column(String, nullable=False) # REVIEW, UNRESOLVED, DUPLICATE_CONFLICT
    confidence = Column(Float, nullable=False)
    
    order_id = Column(String)
    payment_id = Column(String)
    settlement_id = Column(String)
    bank_transaction_id = Column(String)
    
    variance_details = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    run = relationship("ReconciliationRun", back_populates="exceptions")
    evidence = relationship("ExceptionEvidence", back_populates="exception_record", cascade="all, delete-orphan")


class ExceptionEvidence(Base):
    __tablename__ = "exception_evidence"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exception_id = Column(String, ForeignKey("exceptions.id"), nullable=False)
    
    feature_name = Column(String, nullable=False)
    value = Column(Float)
    threshold = Column(Float)
    passed = Column(Integer) # Boolean conceptually, mapped to int for wider compatibility
    explanation = Column(String)
    
    exception_record = relationship("ExceptionRecord", back_populates="evidence")


class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("reconciliation_runs.id"), nullable=True)
    
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    
    metadata_json = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    run = relationship("ReconciliationRun", back_populates="audit_events")
