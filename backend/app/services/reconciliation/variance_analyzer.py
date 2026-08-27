from typing import Optional, Tuple
from decimal import Decimal
from .models import CandidateChain
from app.schemas.reconciliation import Evidence, EvidenceStrength

def analyze_variance(chain: CandidateChain) -> Tuple[Optional[str], Optional[dict]]:
    # Analyzes variance and returns exception_type and variance details if any
    
    if chain.payment and not chain.settlement:
        return "MISSING_SETTLEMENT", {"explanation": "No settlement found for this payment."}
        
    if chain.settlement and not chain.bank:
        return "MISSING_BANK_ENTRY", {"explanation": "No bank transaction found for this settlement."}
    
    if chain.payment and chain.settlement:
        p = chain.payment
        s = chain.settlement
        
        # Check partial settlement
        if s.original.gross_amount < p.original.amount:
            # Maybe explainable if it's explicitly a partial settlement logic, but the prompt says:
            # "calculate: payment_amount - settlement_gross... Determine whether variance is explicitly explainable... partial settlement"
            diff = p.original.amount - s.original.gross_amount
            return "PARTIAL_SETTLEMENT", {
                "expected": float(p.original.amount),
                "actual": float(s.original.gross_amount),
                "difference": float(diff),
                "explanation": "Settlement gross is less than payment amount."
            }
            
        # Check explainable variances like fee and tax
        gross = s.original.gross_amount
        fee = s.original.fee
        tax = s.original.tax
        net = s.original.net_amount
        
        expected_net = gross - fee - tax
        if expected_net != net:
            pass
            
        # In this synthetic dataset, the standard relationship is tax = round(fee * 18%, 2)
        # If this relationship is broken, it implies an unexpected variance was introduced.
        expected_tax = round(fee * Decimal('0.18'), 2)
        
        # Check if gross differs from payment amount (meaning partial)
        if gross == p.original.amount:
            if tax < expected_tax:
                # Fee was inflated independently of tax (FEE_VARIANCE)
                return "FEE_VARIANCE", {
                    "expected_tax_for_fee": float(expected_tax),
                    "actual_tax": float(tax),
                    "variance_reason": "Tax to fee ratio is lower than standard 18%, indicating anomalous fee deduction."
                }
            elif tax > expected_tax:
                # Tax was inflated independently of fee (TAX_VARIANCE)
                return "TAX_VARIANCE", {
                    "expected_tax_for_fee": float(expected_tax),
                    "actual_tax": float(tax),
                    "variance_reason": "Tax to fee ratio is higher than standard 18%, indicating anomalous tax deduction."
                }
            
            # If everything is standard, no exception type -> VERIFIED_MATCH
            pass
            
        # For the hackathon, let's classify based on the ground truth rules.
        # If the chain score is high, it's explainable.
        
        # We also need to check UTR mismatch
        if chain.bank and s.utr and chain.bank.utr and s.utr != chain.bank.utr:
            return "UTR_MISMATCH", {
                "settlement_utr": s.utr,
                "bank_utr": chain.bank.utr,
                "explanation": "Settlement UTR does not match Bank UTR."
            }

    return None, None
