from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import uuid
import time

from app.db.database import get_db
from app.db.models import ReconciliationRun, ReconciliationMatch, ExceptionRecord, ExceptionEvidence, AuditEvent
from app.services.synthetic.generator import DataGenerator
from app.services.reconciliation.thresholds import ReconciliationThresholds
from app.services.reconciliation.engine import reconcile

router = APIRouter(prefix="/api/v1/reconciliation", tags=["reconciliation"])

class RunRequest(BaseModel):
    mode: str = "demo"
    provider: str = "SYNTHETIC"
    size: int = 1000
    seed: int = 42

def execute_reconciliation_run(run_id: str, request: RunRequest):
    from app.db.database import SessionLocal
    import traceback
    
    db = SessionLocal()
    try:
        start_time = time.time()
        
        # 1. Update status to processing
        run_record = db.query(ReconciliationRun).filter(ReconciliationRun.id == run_id).first()
        if not run_record:
            return
            
        run_record.status = "PROCESSING"
        db.commit()
        
        # 2. Fetch Data
        o_list, p_list, s_list, b_list = [], [], [], []
        
        if request.provider == "RAZORPAY_TEST":
            from app.providers.razorpay_provider import RazorpayProvider
            provider = RazorpayProvider()
            o_list, p_list, s_list = provider.fetch_data(limit=request.size)
            # Razorpay doesn't provide bank transactions in this flow
            # For demonstration, b_list remains empty unless we have a BankProvider
        else:
            # Synthetic Data
            provider = DataGenerator(seed=request.seed)
            scenarios = provider.generate(size=request.size)
            gt_map = {}
            for o, p, s, b, gt in scenarios:
                o_list.extend(o)
                p_list.extend(p)
                s_list.extend(s)
                b_list.extend(b)
                gt_map[gt.scenario_id] = gt
            
        # 3. Setup Engine for Demo/Test
        demo_thresholds = ReconciliationThresholds(
            verified_match_min=0.99,
            explainable_variance_min=0.80,
            review_min=0.40,
            ambiguity_margin=0.02
        )
        
        # Build chains and score
        result = reconcile(o_list, p_list, s_list, b_list, thresholds=demo_thresholds)
        
        # 4. Evaluate metrics
        elapsed = result['metrics']['elapsed_seconds']
        throughput = result['metrics']['records_per_second']
        
        # Calculate distribution
        dist = {}
        scenarios = set()
        for r in result['results']:
            if r.order_ids: scenarios.add(r.order_ids[0])
            dist[r.decision] = dist.get(r.decision, 0) + 1
        
        # 5. Persist run results
        run_record.status = "COMPLETED"
        run_record.records_processed = result['metrics']['records_processed']
        run_record.scenario_count = len(result['results'])
        run_record.verified_match = dist.get("VERIFIED_MATCH", 0)
        run_record.explainable_variance = dist.get("MATCH_WITH_EXPLAINABLE_VARIANCE", 0)
        run_record.review = dist.get("REVIEW", 0)
        run_record.unresolved = dist.get("UNRESOLVED", 0)
        run_record.duplicate_conflict = dist.get("DUPLICATE_CONFLICT", 0)
        run_record.elapsed_seconds = elapsed
        run_record.throughput = throughput
        
        # 6. Persist matches and exceptions
        for res in result['results']:
            scen_id = res.order_ids[0] if res.order_ids else None
            oid = res.order_ids[0] if res.order_ids else None
            pid = res.payment_ids[0] if res.payment_ids else None
            sid = res.settlement_ids[0] if res.settlement_ids else None
            bid = res.bank_transaction_ids[0] if res.bank_transaction_ids else None
            
            if res.decision in ["VERIFIED_MATCH", "MATCH_WITH_EXPLAINABLE_VARIANCE"]:
                match = ReconciliationMatch(
                    run_id=run_id,
                    scenario_id=scen_id,
                    decision=res.decision,
                    confidence=res.confidence,
                    order_id=oid,
                    payment_id=pid,
                    settlement_id=sid,
                    bank_transaction_id=bid,
                    variance_details=res.variance_details
                )
                db.add(match)
            else:
                ex = ExceptionRecord(
                    run_id=run_id,
                    scenario_id=scen_id,
                    exception_type=res.exception_type or "UNRESOLVED",
                    decision=res.decision,
                    confidence=res.confidence,
                    order_id=oid,
                    payment_id=pid,
                    settlement_id=sid,
                    bank_transaction_id=bid,
                    variance_details=res.variance_details
                )
                db.add(ex)
                db.flush()
                
                # Add evidence
                for ev_data in res.evidence:
                    val = ev_data.value
                    if isinstance(val, (int, float)):
                        parsed_val = float(val)
                    else:
                        parsed_val = 0.0
                        
                    ev = ExceptionEvidence(
                        exception_id=ex.id,
                        feature_name=ev_data.field,
                        value=parsed_val,
                        passed=0,
                        explanation=ev_data.explanation
                    )
                    db.add(ev)
                
        # 7. Audit Event
        audit = AuditEvent(
            run_id=run_id,
            action="RECORDS_PROCESSED",
            entity_type="Batch",
            entity_id=run_id,
            actor="System",
            metadata_json={"records": result['metrics']['records_processed'], "status": "COMPLETED"}
        )
        db.add(audit)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        run_record = db.query(ReconciliationRun).filter(ReconciliationRun.id == run_id).first()
        if run_record:
            run_record.status = "FAILED"
            db.commit()
        print(f"Run failed: {e}\n{traceback.format_exc()}")
    finally:
        db.close()

@router.post("/run")
def start_reconciliation_run(req: RunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if req.mode == "evaluation":
        raise HTTPException(status_code=403, detail="Evaluation mode cannot be triggered via normal API.")
        
    run_id = str(uuid.uuid4())
    new_run = ReconciliationRun(
        id=run_id,
        mode=req.mode,
        provider=req.provider,
        size=req.size,
        seed=req.seed,
        status="STARTED"
    )
    db.add(new_run)
    
    # Audit Event
    audit = AuditEvent(
        run_id=run_id,
        action="RECONCILIATION_STARTED",
        entity_type="Batch",
        entity_id=run_id,
        actor="System Schedule" if req.mode == "demo" else "User",
        metadata_json={"mode": req.mode, "provider": req.provider}
    )
    db.add(audit)
    db.commit()
    
    background_tasks.add_task(execute_reconciliation_run, run_id, req)
    
    return {
        "run_id": run_id,
        "status": "STARTED"
    }

@router.get("/runs/{run_id}")
def get_run_status(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ReconciliationRun).filter(ReconciliationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return {
        "run_id": run.id,
        "status": run.status,
        "mode": run.mode,
        "records_processed": run.records_processed,
        "scenario_count": run.scenario_count,
        "verified_match": run.verified_match,
        "explainable_variance": run.explainable_variance,
        "review": run.review,
        "unresolved": run.unresolved,
        "duplicate_conflict": run.duplicate_conflict,
        "elapsed_seconds": run.elapsed_seconds,
        "throughput": run.throughput
    }

@router.get("/demo/latest")
def get_latest_demo_run(db: Session = Depends(get_db)):
    run_record = db.query(ReconciliationRun).filter(
        ReconciliationRun.mode == "demo", 
        ReconciliationRun.status == "COMPLETED",
        ReconciliationRun.provider == "SYNTHETIC",
        ReconciliationRun.seed == 42
    ).order_by(ReconciliationRun.created_at.desc()).first()
    
    if not run_record:
        raise HTTPException(status_code=404, detail="No completed demo run found")
    
    return {
        "run_id": run_record.id,
        "status": run_record.status,
        "started_at": run_record.created_at,  # Map to expected frontend field
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
