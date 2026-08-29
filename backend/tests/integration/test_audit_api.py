import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db
from app.db.models import AuditEvent
from unittest.mock import MagicMock

def test_audit_api_empty():
    db_mock = MagicMock()
    db_mock.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
    
    app.dependency_overrides[get_db] = lambda: db_mock
    client = TestClient(app)
    
    res = client.get("/api/v1/audit")
    assert res.status_code == 200
    assert res.json() == []
    app.dependency_overrides.clear()

def test_audit_api_returns_records():
    db_mock = MagicMock()
    evt = AuditEvent(
        id=str(uuid.uuid4()),
        run_id="run-123",
        action="RECONCILIATION_STARTED",
        entity_type="Batch",
        entity_id="run-123",
        actor="System Schedule",
        metadata_json={"mode": "demo"},
        created_at=datetime.utcnow()
    )
    db_mock.query.return_value.order_by.return_value.limit.return_value.all.return_value = [evt]
    
    app.dependency_overrides[get_db] = lambda: db_mock
    client = TestClient(app)
    
    res = client.get("/api/v1/audit")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["action"] == "RECONCILIATION_STARTED"
    assert data[0]["actor"] == "System Schedule"
    assert "created_at" in data[0]
    app.dependency_overrides.clear()
