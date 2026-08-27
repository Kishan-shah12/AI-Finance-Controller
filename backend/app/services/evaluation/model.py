import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import List, Dict
import json
from pathlib import Path
from app.services.reconciliation.models import CandidateChain
from app.services.reconciliation.stage3_scoring import DeterministicLogisticBaseline
from app.schemas.ground_truth import GroundTruthItem

class TrainedLogisticScorer:
    def __init__(self, model_version: str = "trained_v1"):
        self.model = LogisticRegression(random_state=42, class_weight="balanced")
        self.model_version = model_version
        self.baseline = DeterministicLogisticBaseline()
        
    def _extract_features(self, chain: CandidateChain) -> np.ndarray:
        return self.baseline._extract_features(chain)
        
    def train(self, chains: List[CandidateChain], gt_map: Dict[str, GroundTruthItem]):
        # Construct X and y
        X = []
        y = []
        for chain in chains:
            if chain.match_type == "EXACT":
                continue # Skip exact matches for training fuzzy scorer
                
            features = self._extract_features(chain)
            
            # Determine label
            # If the chain's IDs match a TRUE ground truth exactly.
            # We look up the ground truth by payment_id or order_id
            pid = chain.payment.id if chain.payment else None
            oid = chain.order.id if chain.order else None
            
            # Find matching gt
            label = 0
            for gt in gt_map.values():
                if pid and gt.payment_id == pid:
                    if gt.ground_truth_match:
                        # check if settlement matches
                        if chain.settlement and chain.settlement.id != gt.settlement_id:
                            label = 0
                        else:
                            label = 1
                    break
                elif oid and gt.order_id == oid:
                    if gt.ground_truth_match:
                        if chain.payment and chain.payment.id != gt.payment_id:
                            label = 0
                        else:
                            label = 1
                    break
                    
            X.append(features)
            y.append(label)
            
        if X and len(set(y)) > 1:
            self.model.fit(np.array(X), np.array(y))
        else:
            # Fallback if training data is weird
            self.model.coef_ = np.array([[0.2, 0.3, 0.1, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0]])
            self.model.intercept_ = np.array([-0.5])
            self.model.classes_ = np.array([0, 1])

    def score_chain(self, chain: CandidateChain) -> CandidateChain:
        if chain.match_type == "EXACT":
            chain.score = 0.99
            return chain
            
        features = self._extract_features(chain).reshape(1, -1)
        prob = self.model.predict_proba(features)[0][1]
        chain.score = float(prob)
        return chain

    def save_config(self, filepath: Path, thresholds: dict):
        config = {
            "model_version": self.model_version,
            "thresholds": thresholds,
            "feature_version": "v1",
            "dataset_version": "v1",
            "hyperparameters": self.model.get_params()
        }
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
