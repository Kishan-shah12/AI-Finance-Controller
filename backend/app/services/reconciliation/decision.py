from typing import Tuple
from .models import CandidateChain
from .thresholds import thresholds

def make_decision(chain: CandidateChain, exception_type: str = None) -> str:
    # VERIFIED_MATCH, MATCH_WITH_EXPLAINABLE_VARIANCE, REVIEW, UNRESOLVED, DUPLICATE_CONFLICT
    
    if exception_type == "DUPLICATE":
        return "DUPLICATE_CONFLICT"
        
    if exception_type in ["MISSING_SETTLEMENT", "MISSING_BANK_ENTRY"]:
        return "UNRESOLVED"
        
    if chain.score >= thresholds.verified_match_min:
        if exception_type:
            # High confidence but has an exception/variance
            if exception_type in ["FEE_VARIANCE", "TAX_VARIANCE", "TIMING_VARIANCE"]:
                return "MATCH_WITH_EXPLAINABLE_VARIANCE"
            else:
                return "REVIEW" # UTR mismatch, partial settlement with high confidence? Review.
        return "VERIFIED_MATCH"
        
    if chain.score >= thresholds.explainable_variance_min:
        if exception_type in ["FEE_VARIANCE", "TAX_VARIANCE"]:
            return "MATCH_WITH_EXPLAINABLE_VARIANCE"
        return "REVIEW"
        
    if chain.score >= thresholds.review_min:
        return "REVIEW"
        
    return "UNRESOLVED"
