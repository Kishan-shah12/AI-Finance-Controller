import time
from typing import List, Dict, Any
from app.schemas.financial import Order, Payment, Settlement, BankTransaction
from app.schemas.reconciliation import ReconciliationResult

from .normalization import normalize_order, normalize_payment, normalize_settlement, normalize_bank
from .stage1_exact import run_stage1_exact
from .stage2_rules import run_stage2_rules
from .stage3_scoring import run_stage3_scoring
from .variance_analyzer import analyze_variance
from .decision import make_decision
from .thresholds import thresholds, ReconciliationThresholds

def reconcile(
    orders: List[Order], 
    payments: List[Payment], 
    settlements: List[Settlement], 
    banks: List[BankTransaction],
    scorer=None,
    thresholds: ReconciliationThresholds = None
) -> Dict[str, Any]:
    """
    Main reconciliation entrypoint.
    Returns a dictionary with 'results' (list of ReconciliationResult) and 'metrics'.
    """
    start_time = time.time()
    
    if thresholds is None:
        from .thresholds import thresholds as default_thresholds
        thresholds = default_thresholds
    
    # 0. Normalization
    norm_orders = [normalize_order(o) for o in orders]
    norm_payments = [normalize_payment(p) for p in payments]
    norm_settlements = [normalize_settlement(s) for s in settlements]
    norm_banks = [normalize_bank(b) for b in banks]
    
    # 1. Exact Matching
    exact_chains, unmatched = run_stage1_exact(norm_orders, norm_payments, norm_settlements, norm_banks)
    
    # 2. Candidate Generation
    rule_chains, remaining = run_stage2_rules(unmatched, exact_chains)
    
    # Combine chains for scoring
    all_chains = exact_chains + rule_chains
    
    # 3. Scoring
    scored_chains = run_stage3_scoring(all_chains, scorer=scorer)
    
    # 4. Resolve ambiguity & duplication (basic version)
    # Group by payment to find duplicates or ambiguity
    chains_by_payment = {}
    for c in scored_chains:
        if c.payment:
            pid = c.payment.id
            if pid not in chains_by_payment:
                chains_by_payment[pid] = []
            chains_by_payment[pid].append(c)
            
    final_results = []
    
    for pid, chains in chains_by_payment.items():
        if len(chains) == 1:
            chain = chains[0]
            exc_type, var_details = analyze_variance(chain)
            decision = make_decision(chain, exc_type)
            
            res = ReconciliationResult(
                order_ids=[chain.order.id] if chain.order else [],
                payment_ids=[chain.payment.id] if chain.payment else [],
                settlement_ids=[chain.settlement.id] if chain.settlement else [],
                bank_transaction_ids=[chain.bank.id] if chain.bank else [],
                decision=decision,
                confidence=chain.score,
                match_type=chain.match_type,
                exception_type=exc_type,
                variance_details=var_details,
                evidence=chain.evidence,
                processing_timestamp=time.time()
            )
            final_results.append(res)
        else:
            # Ambiguity or Duplicate
            # Sort by score
            chains.sort(key=lambda x: x.score, reverse=True)
            top1 = chains[0]
            top2 = chains[1]
            
            if top1.score - top2.score < thresholds.ambiguity_margin:
                # Ambiguous
                exc_type = "AMBIGUOUS"
                decision = "REVIEW"
            else:
                # Top1 wins
                exc_type, _ = analyze_variance(top1)
                decision = make_decision(top1, exc_type)
                
            res = ReconciliationResult(
                order_ids=[top1.order.id] if top1.order else [],
                payment_ids=[top1.payment.id] if top1.payment else [],
                settlement_ids=[top1.settlement.id] if top1.settlement else [],
                bank_transaction_ids=[top1.bank.id] if top1.bank else [],
                decision=decision,
                confidence=top1.score,
                match_type="AMBIGUOUS_RESOLUTION",
                exception_type=exc_type,
                processing_timestamp=time.time()
            )
            final_results.append(res)
            
    # Handle remaining unmatched records
    for r in remaining:
        # these are unresolved
        res = ReconciliationResult(
            order_ids=[r.id] if r.type == 'order' else [],
            payment_ids=[r.id] if r.type == 'payment' else [],
            settlement_ids=[r.id] if r.type == 'settlement' else [],
            bank_transaction_ids=[r.id] if r.type == 'bank' else [],
            decision="UNRESOLVED",
            confidence=0.0,
            match_type="NONE",
            processing_timestamp=time.time()
        )
        final_results.append(res)

    end_time = time.time()
    elapsed = end_time - start_time
    total_records = len(orders) + len(payments) + len(settlements) + len(banks)
    
    return {
        "results": final_results,
        "metrics": {
            "records_processed": total_records,
            "elapsed_seconds": elapsed,
            "records_per_second": total_records / elapsed if elapsed > 0 else 0
        }
    }
