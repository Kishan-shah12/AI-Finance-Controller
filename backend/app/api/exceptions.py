from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ExceptionRecord, ExceptionEvidence, AuditEvent

router = APIRouter(prefix="/api/v1/exceptions", tags=["exceptions"])

class ActionRequest(BaseModel):
    action: str # APPROVE_MATCH, KEEP_EXCEPTION, ESCALATE

@router.get("/")
def get_exceptions(db: Session = Depends(get_db)):
    records = db.query(ExceptionRecord).all()
    # Format for frontend
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "decision": r.decision,
            "exception_type": r.exception_type,
            "confidence": r.confidence,
            "variance_details": r.variance_details,
            "evidence": [] # simplified for list
        })
    return result

def get_demo_priority_score(exception: ExceptionRecord) -> float:
    # Priority considers: 1. severity, 2. financial impact, 3. uncertainty, 4. exception type
    
    # Base score by exception type (severity)
    severity_map = {
        "AMBIGUOUS": 10000,
        "UNRESOLVED": 8000,
        "MISSING_SETTLEMENT": 6000,
        "REVIEW": 4000,
        "PARTIAL_SETTLEMENT": 2000
    }
    
    # Default severity for unknown types
    score = severity_map.get(exception.exception_type, 1000)
    
    # Financial impact (amount difference)
    # Assume variance_details has "amount_difference" if applicable
    amount_diff = 0
    if exception.variance_details and isinstance(exception.variance_details, dict):
        amount_diff = abs(float(exception.variance_details.get("amount_difference", 0)))
        
    # Scale amount difference so it adds meaningfully to severity but doesn't override major categories unless huge
    score += min(amount_diff, 1999) 
    
    # Uncertainty (lower confidence = higher priority)
    # We add up to 100 points based on how low the confidence is.
    uncertainty_bonus = (1.0 - (exception.confidence or 1.0)) * 100
    score += uncertainty_bonus
    
    return float(score)

@router.get("/run/{run_id}/highest-priority")
def get_highest_priority_exception(run_id: str, db: Session = Depends(get_db)):
    # Find all exceptions for this run that are unresolved or review
    records = db.query(ExceptionRecord).filter(
        ExceptionRecord.run_id == run_id,
        ExceptionRecord.decision.in_(["REVIEW", "UNRESOLVED"])
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No actionable exceptions found for this run")
        
    # Sort deterministically by priority score, then by ID to break ties
    sorted_records = sorted(records, key=lambda r: (get_demo_priority_score(r), r.id), reverse=True)
    
    highest = sorted_records[0]
    return {"id": highest.id}

@router.get("/{id}")
def get_exception(id: str, db: Session = Depends(get_db)):
    record = db.query(ExceptionRecord).filter(ExceptionRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    evidence_records = db.query(ExceptionEvidence).filter(ExceptionEvidence.exception_id == id).all()
    evidence_list = []
    for ev in evidence_records:
        evidence_list.append({
            "feature_name": ev.feature_name,
            "value": ev.value,
            "passed": bool(ev.passed),
            "explanation": ev.explanation
        })
        
    return {
        "id": record.id,
        "decision": record.decision,
        "exception_type": record.exception_type,
        "confidence": record.confidence,
        "variance_details": record.variance_details,
        "evidence": evidence_list
    }

@router.post("/{id}/action")
def perform_action(id: str, req: ActionRequest, db: Session = Depends(get_db)):
    valid_actions = ["APPROVE_MATCH", "KEEP_EXCEPTION", "ESCALATE"]
    if req.action not in valid_actions:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    record = db.query(ExceptionRecord).filter(ExceptionRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    # Validation logic: e.g. you can't approve an already resolved one, etc.
    if record.decision == "VERIFIED_MATCH":
        raise HTTPException(status_code=400, detail="Exception is already resolved")
        
    # Perform action
    if req.action == "APPROVE_MATCH":
        record.decision = "VERIFIED_MATCH"
    elif req.action == "ESCALATE":
        record.decision = "ESCALATED"
        
    # Create audit event
    audit = AuditEvent(
        run_id=record.run_id,
        action="MANUAL_OVERRIDE" if req.action == "APPROVE_MATCH" else "EXCEPTION_ACTION",
        entity_type="Exception",
        entity_id=record.id,
        actor="Finance Controller",
        metadata_json={"action": req.action, "previous_state": record.decision}
    )
    db.add(audit)
    db.commit()
    
    return {"status": "SUCCESS"}
