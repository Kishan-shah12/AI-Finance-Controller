from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import AuditEvent

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

@router.get("/")
def get_audit_events(limit: int = Query(50, le=100), db: Session = Depends(get_db)):
    records = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "run_id": r.run_id,
            "action": r.action,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "actor": r.actor,
            "metadata_json": r.metadata_json,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
