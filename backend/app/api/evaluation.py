import json
from pathlib import Path
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])

@router.get("/final")
def get_final_evaluation():
    backend_dir = Path(__file__).resolve().parent.parent.parent
    eval_dir = backend_dir / 'evaluation' / 'final'
    metrics_path = eval_dir / 'metrics.json'
    config_path = eval_dir / 'evaluation_config.json'
    
    if not metrics_path.exists() or not config_path.exists():
        raise HTTPException(status_code=404, detail="Final evaluation not found")
        
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
        
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    return {
        "dataset_version": config.get("dataset_version"),
        "model_version": config.get("model_version"),
        "total_scenarios": metrics.get("total_scenarios"),
        "operational_match_rate": metrics.get("operational_match_rate"),
        "strict_verified_match_rate": metrics.get("strict_verified_match_rate"),
        "auto_match_rate": metrics.get("auto_match_rate"),
        "precision": metrics.get("precision"),
        "recall": metrics.get("recall"),
        "f1": metrics.get("f1"),
        "false_match_rate": metrics.get("false_match_rate"),
        "review_rate": metrics.get("review_rate"),
        "exception_rate": metrics.get("exception_rate"),
        "throughput": metrics.get("core_engine_throughput")
    }
