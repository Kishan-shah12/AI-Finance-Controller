import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool

# Setup test database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Mock SessionLocal for background tasks
from app.db import database as mock_db
mock_db.SessionLocal = TestingSessionLocal

client = TestClient(app)

def test_razorpay_run_empty_data():
    # 1. Trigger Razorpay run
    res = client.post("/api/v1/reconciliation/run", json={
        "mode": "run",
        "provider": "RAZORPAY_TEST",
        "size": 100,
        "seed": 42
    })
    
    assert res.status_code == 200
    run_id = res.json()["run_id"]
    
    # Give the background task time to run
    import time
    time.sleep(1)
    
    # 2. Check run metrics
    res_status = client.get(f"/api/v1/reconciliation/runs/{run_id}")
    assert res_status.status_code == 200
    data = res_status.json()
    
    assert data["status"] == "COMPLETED"
    
    # The actual provider fetched 0 records.
    assert data["records_processed"] == 0
    # Engine made 0 decisions, so scenario_count should be 0.
    assert data["scenario_count"] == 0
    
    # Decisions should all be 0
    assert data["verified_match"] == 0
    assert data["explainable_variance"] == 0
    assert data["review"] == 0
    assert data["unresolved"] == 0
    assert data["duplicate_conflict"] == 0
    
    # 3. Verify no exceptions are created
    res_exc = client.get(f"/api/v1/exceptions", params={"run_id": run_id})
    assert res_exc.status_code == 200
    assert len(res_exc.json()) == 0

def test_synthetic_run_preserves_size():
    # Trigger synthetic run
    res = client.post("/api/v1/reconciliation/run", json={
        "mode": "demo",
        "provider": "SYNTHETIC",
        "size": 10,
        "seed": 42
    })
    
    assert res.status_code == 200
    run_id = res.json()["run_id"]
    
    import time
    time.sleep(1)
    
    res_status = client.get(f"/api/v1/reconciliation/runs/{run_id}")
    assert res_status.status_code == 200
    data = res_status.json()
    
    assert data["status"] == "COMPLETED"
    assert data["scenario_count"] >= 10
    assert data["records_processed"] > 0
