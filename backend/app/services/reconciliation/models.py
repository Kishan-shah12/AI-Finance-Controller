from typing import Optional
from dataclasses import dataclass, field
from decimal import Decimal
from app.schemas.financial import Order, Payment, Settlement, BankTransaction

@dataclass
class NormalizedRecord:
    type: str  # 'order', 'payment', 'settlement', 'bank'
    id: str
    merchant_id: str
    amount: Decimal
    date: float  # timestamp for easy comparison
    utr: Optional[str] = None
    original: object = None

@dataclass
class CandidateChain:
    order: Optional[NormalizedRecord] = None
    payment: Optional[NormalizedRecord] = None
    settlement: Optional[NormalizedRecord] = None
    bank: Optional[NormalizedRecord] = None
    
    score: float = 0.0
    match_type: str = ""
    evidence: list = field(default_factory=list)
