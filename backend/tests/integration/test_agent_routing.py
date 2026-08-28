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
    ex1.order_id = "TX-1"
    
    db.query.return_value.filter.return_value.limit.return_value.all.return_value = [ex1]
    return db

def test_agent_routing_greeting(db_session):
    agent_service = AgentService()
    
    result = agent_service.process_query("hello there", db_session, {})
    assert result["status"] == "SUCCESS"
    assert "Hello!" in result["answer"]
    assert result["evidence"] is None
    assert result["confidence"] is None
    assert result["provider_metadata"] == "Agent router"

def test_agent_routing_capabilities(db_session):
    agent_service = AgentService()
    
    result = agent_service.process_query("what can you do", db_session, {})
    assert result["status"] == "SUCCESS"
    assert "analyze settlement variances" in result["answer"]
    assert result["evidence"] is None
    assert result["confidence"] is None
    assert result["provider_metadata"] == "Agent router"

def test_agent_routing_shortfall(db_session):
    agent_service = AgentService()
    
    result = agent_service.process_query("Why is today's settlement short?", db_session, {})
    assert result["status"] == "SUCCESS"
    if result["evidence"]:
        assert "exception_id" in result["evidence"][0]
        assert "transaction_id" not in result["evidence"][0]

def test_agent_routing_unresolved(db_session):
    agent_service = AgentService()
    result = agent_service.process_query("Show unresolved transactions above 10,000", db_session, {})
    assert result["status"] == "SUCCESS"
    if result["evidence"]:
        assert "exception_id" in result["evidence"][0]

def test_agent_routing_safe_auto_close(db_session):
    agent_service = AgentService()
    result = agent_service.process_query("which records are safe to auto-close?", db_session, {})
    assert result["status"] == "SUCCESS"
    if result["evidence"]:
        assert "exception_id" in result["evidence"][0]
        assert result["evidence"][0]["passed"] is True

def test_agent_routing_other(db_session):
    agent_service = AgentService()
    result = agent_service.process_query("how is the weather?", db_session, {})
    assert result["status"] == "SUCCESS"
    assert "I can help with" in result["answer"]
    assert result["evidence"] is None
    assert result["confidence"] is None
    assert result["provider_metadata"] == "Agent router"

