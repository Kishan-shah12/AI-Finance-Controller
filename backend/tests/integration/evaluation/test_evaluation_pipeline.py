import json
from pathlib import Path
from app.services.evaluation.dataset import load_split

def test_metrics_consistency():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    eval_dir = root_dir / 'backend' / 'evaluation' / 'final'
    metrics_path = eval_dir / 'metrics.json'
    
    assert metrics_path.exists(), "Metrics file must be generated"
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
        
    assert "total_scenarios" in metrics
    assert "standard_precision" in metrics
    assert metrics["standard_precision"] is not None
    assert metrics["operational_match_rate"] is not None
    
    # 8. Division by zero check -> NaNs check
    for k, v in metrics.items():
        if isinstance(v, float):
            assert v == v, f"NaN found in metric {k}"

def test_decision_distribution_sum():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    eval_dir = root_dir / 'backend' / 'evaluation' / 'final'
    metrics_path = eval_dir / 'metrics.json'
    dist_path = eval_dir / 'decision_distribution.json'
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
        
    with open(dist_path, 'r') as f:
        dist = json.load(f)
        
    total_decisions = sum(dist.values())
    assert total_decisions == metrics["total_scenarios"], "Decision counts must sum to total scenarios exactly"

def test_ground_truth_isolation():
    # Test that backend/app code (engine) does NOT import ground truth
    import ast
    engine_path = Path(__file__).resolve().parent.parent.parent.parent / 'app' / 'services' / 'reconciliation'
    
    for py_file in engine_path.glob("*.py"):
        with open(py_file, 'r') as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "ground_truth" not in alias.name, f"Engine file {py_file.name} violates ground truth isolation!"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "ground_truth" not in node.module, f"Engine file {py_file.name} violates ground truth isolation!"

def test_metric_formulas():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    eval_dir = root_dir / 'backend' / 'evaluation' / 'final'
    metrics_path = eval_dir / 'metrics.json'
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
        
    p = metrics["standard_precision"]
    r = metrics["overall_match_recall"]
    f1 = metrics["standard_f1"]
    
    if p + r > 0:
        expected_f1 = 2 * p * r / (p + r)
        assert abs(f1 - expected_f1) < 1e-5, "Standard F1 formula is incorrect!"
        
    safe_p = metrics["safe_auto_match_precision"]
    safe_r = metrics["safe_auto_match_recall"]
    
    # Safe auto-match recall denominator is strictly smaller, so recall should be higher or equal
    assert safe_r >= r, "Safe auto-match recall should be >= overall match recall"
    
def test_frozen_configuration():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    eval_dir = root_dir / 'backend' / 'evaluation' / 'final'
    config_path = eval_dir / 'evaluation_config.json'
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    # Test that frozen configuration remained unchanged
    assert config["thresholds"]["explainable_variance_min"] == 0.80
    assert config["thresholds"]["review_min"] == 0.40
    assert config["thresholds"]["ambiguity_margin"] == 0.02
    assert config["model_version"] == "trained_v1"
