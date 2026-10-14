import os
import uuid
import json
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

backend_dir = Path(__file__).resolve().parent.parent.parent
default_sqlite_path = backend_dir / "reconai.db"

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

def get_engine_and_session():
    global engine, SessionLocal
    url = DATABASE_URL
    
    if url:
        try:
            connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
            eng = create_engine(url, connect_args=connect_args)
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine = eng
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            print(f"Connected to database using {url.split('@')[-1] if '@' in url else url.split('://')[0]}")
            return
        except Exception as e:
            print(f"Configured DATABASE_URL failed: {e}. Falling back to local SQLite.")
            
    # Default to local SQLite database
    sqlite_url = f"sqlite:///{default_sqlite_path}"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"Using local SQLite database at {default_sqlite_path}")

get_engine_and_session()

def get_db():
    if not SessionLocal:
        raise RuntimeError("Database is unavailable. Configure DATABASE_URL.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_initial_data_if_needed():
    if not SessionLocal:
        return
    db = SessionLocal()
    try:
        from app.db.models import ReconciliationRun, ExceptionRecord, ExceptionEvidence, AuditEvent
        
        # Check if already seeded
        if db.query(ExceptionRecord).count() > 0:
            return
            
        report_path = backend_dir / "evaluation" / "final" / "exception_report.json"
        metrics_path = backend_dir / "evaluation" / "final" / "metrics.json"
        if not report_path.exists():
            return
            
        with open(report_path, "r") as f:
            exceptions_data = json.load(f)
            
        metrics = {}
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
                
        # Create initial demo run
        initial_run_id = "demo-run-canonical-v1"
        existing_run = db.query(ReconciliationRun).filter(ReconciliationRun.id == initial_run_id).first()
        if not existing_run:
            demo_run = ReconciliationRun(
                id=initial_run_id,
                mode="demo",
                provider="SYNTHETIC",
                status="COMPLETED",
                size=1000,
                seed=42,
                records_processed=metrics.get("total_scenarios", 1000),
                scenario_count=metrics.get("total_scenarios", 1000),
                verified_match=int(metrics.get("total_scenarios", 1000) * metrics.get("strict_verified_match_rate", 0.94)),
                explainable_variance=int(metrics.get("total_scenarios", 1000) * (metrics.get("operational_match_rate", 0.98) - metrics.get("strict_verified_match_rate", 0.94))),
                review=int(metrics.get("total_scenarios", 1000) * metrics.get("review_rate", 0.01)),
                unresolved=len(exceptions_data),
                elapsed_seconds=1.2,
                throughput=metrics.get("core_engine_throughput", 850.0)
            )
            db.add(demo_run)
            
            # Initial audit event
            audit = AuditEvent(
                id=str(uuid.uuid4()),
                run_id=initial_run_id,
                action="INITIAL_SEED",
                entity_type="ReconciliationRun",
                entity_id=initial_run_id,
                actor="System",
                metadata_json={"source": "evaluation/final"}
            )
            db.add(audit)
            db.commit()
            
        # Seed exceptions
        for idx, ex in enumerate(exceptions_data):
            ex_id = f"EX-{1000 + idx}"
            variance = ex.get("variance_details") or {}
            
            # Determine amount from evidence or variance if available
            amt_diff = variance.get("amount_difference") or variance.get("difference")
            if amt_diff is None:
                amt_diff = 4500.0 + (idx * 350.0)
                variance["amount_difference"] = amt_diff
                variance["expected"] = amt_diff
                variance["actual"] = 0.0
                
            exc_type = ex.get("exception_type") or "UNRESOLVED"
            exc_record = ExceptionRecord(
                id=ex_id,
                run_id=initial_run_id,
                scenario_id=f"SCENARIO-{1000 + idx}",
                exception_type=exc_type,
                decision=ex.get("decision", "UNRESOLVED"),
                confidence=float(ex.get("confidence", 0.85) or 0.85),
                order_id=f"ORD-{500 + idx}",
                payment_id=f"PAY-{500 + idx}",
                settlement_id=f"SETTLE-{500 + idx}" if "MISSING_SETTLEMENT" not in exc_type else None,
                bank_transaction_id=f"BANK-{500 + idx}" if "MISSING_BANK" not in exc_type else None,
                variance_details=variance
            )
            db.add(exc_record)
            
            # Seed evidence
            ev_list = ex.get("evidence") or []
            if not ev_list:
                ev_list = [
                    {"field": "amount_match", "strength": "FAILED", "explanation": variance.get("explanation", "Variance exceeds tolerance threshold.")}
                ]
            for ev in ev_list:
                evidence = ExceptionEvidence(
                    id=str(uuid.uuid4()),
                    exception_id=ex_id,
                    feature_name=ev.get("field") or ev.get("source") or "reconciliation_feature",
                    value=0.25 if ev.get("strength") in ["FAILED", "WEAK"] else 0.95,
                    threshold=0.80,
                    passed=0 if ev.get("strength") in ["FAILED", "WEAK"] else 1,
                    explanation=ev.get("explanation") or f"Verification feature {ev.get('field', 'check')} evaluated."
                )
                db.add(evidence)
                
        db.commit()
        print(f"Successfully seeded {len(exceptions_data)} initial exceptions into database.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding initial data: {e}")
    finally:
        db.close()

def init_db():
    if engine:
        Base.metadata.create_all(bind=engine)
        seed_initial_data_if_needed()
