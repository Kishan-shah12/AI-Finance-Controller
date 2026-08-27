# thresholds.py
from pydantic_settings import BaseSettings

class ReconciliationThresholds(BaseSettings):
    verified_match_min: float = 0.90
    explainable_variance_min: float = 0.80
    review_min: float = 0.50
    ambiguity_margin: float = 0.05

thresholds = ReconciliationThresholds()
