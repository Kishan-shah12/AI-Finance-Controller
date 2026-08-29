from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_evaluation_api_contract():
    res = client.get("/api/v1/evaluation/final")
    assert res.status_code == 200
    data = res.json()
    
    # Assert Exact Field Names Expected by Frontend MetricData
    expected_fields = [
        "dataset_version",
        "model_version",
        "total_scenarios",
        "operational_match_rate",
        "strict_verified_match_rate",
        "auto_match_rate",
        "standard_precision",
        "overall_match_recall",
        "standard_f1",
        "safe_auto_match_precision",
        "safe_auto_match_recall",
        "false_match_rate",
        "review_rate",
        "exception_rate",
        "core_engine_throughput"
    ]
    
    for field in expected_fields:
        assert field in data, f"Missing required metric field: {field}"
        assert data[field] is not None, f"Metric field {field} is null"
