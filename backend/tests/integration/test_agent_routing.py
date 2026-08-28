import pytest
from app.services.agent.llm import AgentService
from app.db.database import SessionLocal
from app.db.models import ReconciliationRun, ExceptionRecord

from unittest.mock import MagicMock

@pytest.fixture
def db_session():
    # Return a mocked Session
    db = MagicMock()
    # Mock the query chain: db.query().filter().order_by().first()
    latest_run_mock = MagicMock()
    latest_run_mock.id = "mock_run_id"
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = latest_run_mock
    
    # Mock exceptions for routing
    ex1 = MagicMock()
    ex1.id = "ex-1"
    ex1.exception_type = "Fee Variance"
    ex1.confidence = 0.8
    ex1.transaction_id = "TX-1"
    
    db.query.return_value.filter.return_value.limit.return_value.all.return_value = [ex1]
    
    return db

def test_agent_fallback_routing_greeting(db_session):
    agent_service = AgentService()
    # Force fallback provider
    agent_service.gemini_key = None
    agent_service.nemotron_key = None
    
    result = agent_service.process_query("hi", db_session, {})
    assert result["status"] == "SUCCESS"
    assert "Hello" in result["answer"]
    assert len(result["evidence"]) == 0
    assert result["confidence"] is None

def test_agent_fallback_routing_shortfall(db_session):
    agent_service = AgentService()
    
    # We rely on DB state being populated by the synthetic engine in other tests.
    result = agent_service.process_query("Why is today's settlement short?", db_session, {})
    assert result["status"] == "SUCCESS"
    # Even if DB is empty, the logic shouldn't crash.
    # If it found evidence, it must have exception_id
    if len(result["evidence"]) > 0:
        assert "exception_id" in result["evidence"][0]
        assert "confidence" in result

def test_agent_fallback_routing_unresolved(db_session):
    agent_service = AgentService()
    result = agent_service.process_query("Show unresolved transactions above 10,000", db_session, {})
    assert result["status"] == "SUCCESS"
    if len(result["evidence"]) > 0:
        assert "exception_id" in result["evidence"][0]

