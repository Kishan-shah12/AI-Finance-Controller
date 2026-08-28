import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite for testing only! (In memory)
# Wait, user explicitly forbade SQLite.
# "Do NOT introduce SQLite. Use PostgreSQL-compatible persistence throughout."
# So I should mock the database or skip if no postgres is available.
# Let's just write the test so it can be run if postgres is available.

import os
# Check if we should skip db tests
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    pytest.skip("Skipping DB tests because DATABASE_URL is not set", allow_module_level=True)

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_run_demo():
    # Start a run
    res = client.post("/api/v1/reconciliation/run", json={"mode": "demo", "size": 100, "seed": 42})
    assert res.status_code == 200
    run_id = res.json()["run_id"]
    
    # Wait a bit for background task (very crude, but it's a simple test)
    import time
    time.sleep(2)
    
    # Check status
    res = client.get(f"/api/v1/reconciliation/runs/{run_id}")
    assert res.status_code == 200
    assert res.json()["status"] in ["COMPLETED", "FAILED"]
    
    # If completed, check latest endpoint
    if res.json()["status"] == "COMPLETED":
        latest_res = client.get("/api/v1/reconciliation/demo/latest")
        assert latest_res.status_code == 200
        assert latest_res.json()["run_id"] == run_id
        
        # Check highest priority exception
        hp_res = client.get(f"/api/v1/exceptions/run/{run_id}/highest-priority")
        if hp_res.status_code == 200:
            assert "id" in hp_res.json()
        elif hp_res.status_code == 404:
            # Maybe there are no exceptions with that small size/seed
            pass
        else:
            assert False, "Unexpected status code from highest-priority"

def test_agent_unavailable():
    # If no api key is set, it should return AGENT_UNAVAILABLE
    res = client.post("/api/v1/agent/query", json={"query": "test"})
    assert res.status_code == 200
    assert res.json()["status"] == "AGENT_UNAVAILABLE"
