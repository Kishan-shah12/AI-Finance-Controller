from enum import Enum
from pydantic import BaseModel
from typing import Optional

class RecordStatus(str, Enum):
    MATCHABLE = "MATCHABLE"
    NON_MATCHABLE = "NON_MATCHABLE"

class ExpectedDecision(str, Enum):
    VERIFIED_MATCH = "VERIFIED_MATCH"
    MATCH_WITH_EXPLAINABLE_VARIANCE = "MATCH_WITH_EXPLAINABLE_VARIANCE"
    REVIEW = "REVIEW"
    UNRESOLVED = "UNRESOLVED"
    DUPLICATE_CONFLICT = "DUPLICATE_CONFLICT"

class ExceptionType(str, Enum):
    FEE_VARIANCE = "FEE_VARIANCE"
    TAX_VARIANCE = "TAX_VARIANCE"
    MISSING_SETTLEMENT = "MISSING_SETTLEMENT"
    MISSING_BANK_ENTRY = "MISSING_BANK_ENTRY"
    DUPLICATE = "DUPLICATE"
    UTR_MISMATCH = "UTR_MISMATCH"
    PARTIAL_SETTLEMENT = "PARTIAL_SETTLEMENT"
    AMBIGUOUS = "AMBIGUOUS"

class GroundTruthItem(BaseModel):
    scenario_id: str
    scenario_type: str
    record_status: RecordStatus
    
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    settlement_id: Optional[str] = None
    bank_transaction_id: Optional[str] = None
    
    ground_truth_match: bool
    expected_decision: ExpectedDecision
    exception_type: Optional[ExceptionType] = None
    expected_relationships: list[str] = []
