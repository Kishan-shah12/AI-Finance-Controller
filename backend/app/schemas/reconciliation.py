from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class EvidenceStrength(str, Enum):
    STRONG = "STRONG"
    MEDIUM = "MEDIUM"
    WEAK = "WEAK"

class Evidence(BaseModel):
    source: str
    field: str
    value: Any
    strength: EvidenceStrength
    explanation: Optional[str] = None

class ReconciliationResult(BaseModel):
    candidate_id: Optional[str] = None
    order_ids: List[str] = []
    payment_ids: List[str] = []
    settlement_ids: List[str] = []
    bank_transaction_ids: List[str] = []
    
    decision: str
    confidence: float
    match_type: str
    exception_type: Optional[str] = None
    variance_details: Optional[Dict[str, Any]] = None
    evidence: List[Evidence] = []
    
    model_version: str = "1.0"
    rule_version: str = "1.0"
    processing_timestamp: datetime
