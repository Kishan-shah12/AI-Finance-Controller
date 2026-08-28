import os
import sys
from app.db.database import SessionLocal
from app.db.models import ReconciliationRun
try:
    db = SessionLocal()
    run_record = db.query(ReconciliationRun).filter(
        ReconciliationRun.mode == "demo", 
        ReconciliationRun.status == "COMPLETED",
        ReconciliationRun.provider == "SYNTHETIC",
        ReconciliationRun.seed == 42
    ).order_by(ReconciliationRun.created_at.desc()).first()
    print("Record found:", run_record.id if run_record else None)
    
    if run_record:
        # test serialization
        res = {
            "run_id": run_record.id,
            "status": run_record.status,
            "started_at": run_record.created_at,
            "records_processed": run_record.records_processed,
            "scenario_count": run_record.scenario_count,
            "verified_match": run_record.verified_match,
            "explainable_variance": run_record.explainable_variance,
            "review": run_record.review,
            "unresolved": run_record.unresolved,
            "duplicate_conflict": run_record.duplicate_conflict,
            "elapsed_seconds": run_record.elapsed_seconds,
            "throughput": run_record.throughput
        }
        print("Serialization test OK")
        
        # In FastAPI, standard library json is not used directly, but let's test if datetime is serializable
        from fastapi.encoders import jsonable_encoder
        print(jsonable_encoder(res))
except Exception as e:
    import traceback
    traceback.print_exc()
