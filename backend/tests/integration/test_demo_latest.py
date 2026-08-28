import pytest
import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import ReconciliationRun

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    pytest.skip("Skipping DB tests because DATABASE_URL is not set", allow_module_level=True)

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    # Clean the reconciliation_runs table before each test
    db = TestingSessionLocal()
    db.query(ReconciliationRun).delete()
    db.commit()
    db.close()

def test_no_completed_demo_run():
    # A. no completed demo run → 404
    res = client.get("/api/v1/reconciliation/demo/latest")
    assert res.status_code == 404
    assert res.json()["detail"] == "No completed demo run found"

def test_one_completed_demo_run():
    # B. one completed demo run → 200
    # E. nullable fields (size, records_processed, etc can be tested implicitly if we provide minimal data or None)
    # F. response serialization
    db = TestingSessionLocal()
    run = ReconciliationRun(
        id=str(uuid.uuid4()),
        mode="demo",
        provider="SYNTHETIC",
        status="COMPLETED",
        seed=42,
        records_processed=100,
        scenario_count=100,
        verified_match=90,
        explainable_variance=5,
        review=3,
        unresolved=2,
        duplicate_conflict=0,
        elapsed_seconds=1.5,
        throughput=66.6,
        created_at=datetime.utcnow()
    )
    db.add(run)
    db.commit()
    db.close()

    res = client.get("/api/v1/reconciliation/demo/latest")
    assert res.status_code == 200
    data = res.json()
    assert data["run_id"] == run.id
    assert data["status"] == "COMPLETED"
    assert data["records_processed"] == 100
    assert "started_at" in data

def test_multiple_runs_returns_latest():
    # C. multiple runs → latest completed demo run
    db = TestingSessionLocal()
    now = datetime.utcnow()
    
    run_old = ReconciliationRun(
        id=str(uuid.uuid4()),
        mode="demo",
        provider="SYNTHETIC",
        status="COMPLETED",
        seed=42,
        created_at=now - timedelta(days=1)
    )
    run_new = ReconciliationRun(
        id=str(uuid.uuid4()),
        mode="demo",
        provider="SYNTHETIC",
        status="COMPLETED",
        seed=42,
        created_at=now
    )
    db.add_all([run_old, run_new])
    db.commit()
    db.close()

    res = client.get("/api/v1/reconciliation/demo/latest")
    assert res.status_code == 200
    assert res.json()["run_id"] == run_new.id

def test_razorpay_run_is_not_returned():
    # D. Razorpay run is not returned
    db = TestingSessionLocal()
    run_rzp = ReconciliationRun(
        id=str(uuid.uuid4()),
        mode="demo",
        provider="RAZORPAY_TEST",
        status="COMPLETED",
        seed=42
    )
    db.add(run_rzp)
    db.commit()
    db.close()

    res = client.get("/api/v1/reconciliation/demo/latest")
    assert res.status_code == 404

def test_cors_origin_allowed():
    # G. allowed Vercel CORS origin
    headers = {
        "Origin": "https://reconai-gamma.vercel.app"
    }
    res = client.options("/api/v1/reconciliation/demo/latest", headers=headers)
    # The preflight response should include the CORS header
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "https://reconai-gamma.vercel.app"
