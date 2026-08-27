import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import List
from rapidfuzz import fuzz
from .models import CandidateChain

class DeterministicLogisticBaseline:
    """
    Deterministic Logistic-Style Baseline
    This is an explainable and deterministic baseline model for Phase 5.
    It uses manually specified weights to simulate a trained LogisticRegression model
    without importing ground truth or requiring a .pkl file.
    Designed to be a drop-in replacement for a real ML model in Phase 6.
    """
    def __init__(self):
        # We manually initialize a Logistic Regression model for deterministic scoring
        self.model = LogisticRegression()
        self.model.coef_ = np.array([[0.2, 0.3, 0.1, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0]])
        self.model.intercept_ = np.array([-0.5])
        self.model.classes_ = np.array([0, 1])
        
    def _extract_features(self, chain: CandidateChain) -> np.ndarray:
        # id_similarity
        id_sim = 1.0 if chain.match_type == "EXACT" else 0.5 
        # amount_similarity
        amt_sim = 1.0 # default
        if chain.payment and chain.settlement:
            # 1 - |diff|/max
            diff = abs(chain.payment.amount - chain.settlement.amount)
            mx = max(chain.payment.amount, chain.settlement.amount)
            if mx > 0:
                amt_sim = float(1 - diff / mx)
                
        # fee, tax consistency (boolean/float)
        fee_cons = 1.0
        tax_cons = 1.0
        
        # date proximity
        date_prox = 1.0
        if chain.payment and chain.settlement:
            diff_days = abs(chain.settlement.date - chain.payment.date) / 86400
            date_prox = np.exp(-diff_days) # Gaussian-like decay
            
        features = [
            id_sim, amt_sim, date_prox, 1.0, fee_cons, tax_cons, 1.0, 1.0, 1.0, 1.0
        ]
        return np.array(features)

    def score_chain(self, chain: CandidateChain) -> CandidateChain:
        if chain.match_type == "EXACT":
            chain.score = 0.99
            return chain
            
        features = self._extract_features(chain).reshape(1, -1)
        # Using the manual logistic regression to get a probability
        prob = self.model.predict_proba(features)[0][1]
        chain.score = float(prob)
        return chain

def run_stage3_scoring(chains: List[CandidateChain], scorer=None) -> List[CandidateChain]:
    if scorer is None:
        scorer = DeterministicLogisticBaseline()
    for chain in chains:
        scorer.score_chain(chain)
    return chains
