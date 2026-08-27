from typing import List, Dict, Tuple
from collections import defaultdict
from .models import NormalizedRecord, CandidateChain
from app.schemas.reconciliation import Evidence, EvidenceStrength

def run_stage1_exact(orders: List[NormalizedRecord], payments: List[NormalizedRecord], settlements: List[NormalizedRecord], banks: List[NormalizedRecord]) -> Tuple[List[CandidateChain], List[NormalizedRecord]]:
    # Exact matching logic
    # Find links based on exact IDs and UTRs
    
    order_by_id = {o.id: o for o in orders}
    payment_by_id = {p.id: p for p in payments}
    settlement_by_id = {s.id: s for s in settlements}
    
    # Mapping for exact links
    payment_to_order = defaultdict(list)
    for p in payments:
        if hasattr(p.original, 'order_id') and p.original.order_id in order_by_id:
            payment_to_order[p.id].append(order_by_id[p.original.order_id])

    settlement_to_payment = defaultdict(list)
    for s in settlements:
        if hasattr(s.original, 'payment_id') and s.original.payment_id in payment_by_id:
            settlement_to_payment[s.id].append(payment_by_id[s.original.payment_id])

    bank_to_settlement = defaultdict(list)
    settlement_by_utr = defaultdict(list)
    for s in settlements:
        if s.utr:
            settlement_by_utr[(s.merchant_id, s.utr)].append(s)
            
    for b in banks:
        if b.utr:
            matches = settlement_by_utr.get((b.merchant_id, b.utr), [])
            bank_to_settlement[b.id].extend(matches)

    # Build exact chains
    chains = []
    used_records = set()
    
    # For every payment, try to build a chain
    for p in payments:
        ords = payment_to_order[p.id]
        if len(ords) > 1:
            # Duplicate conflict - handled later or mark here? Let's just build all possible exact combinations for now
            pass
            
    # To keep it simple and O(N), let's just group by payment_id
    # Since payment is the central pivot between order and settlement.
    
    # Let's index everything by payment_id
    payment_chains = {}
    for p in payments:
        c = CandidateChain(payment=p, score=0.99, match_type="EXACT")
        ords = payment_to_order.get(p.id, [])
        if len(ords) == 1:
            c.order = ords[0]
            used_records.add(c.order.id)
            c.evidence.append(Evidence(source="payment", field="order_id", value=p.original.order_id, strength=EvidenceStrength.STRONG))
        payment_chains[p.id] = c
        used_records.add(p.id)
        
    for s in settlements:
        pays = settlement_to_payment.get(s.id, [])
        if len(pays) == 1:
            pid = pays[0].id
            if pid in payment_chains:
                payment_chains[pid].settlement = s
                used_records.add(s.id)
                payment_chains[pid].evidence.append(Evidence(source="settlement", field="payment_id", value=s.original.payment_id, strength=EvidenceStrength.STRONG))
            else:
                # Settlement matches payment but payment was processed? Should not happen since we iterated all payments.
                pass
        else:
            # Orphan settlement
            pass
            
    # Now attach banks to settlements
    # A bank attaches to a settlement if they have the exact same UTR.
    orphan_settlement_chains = {}
    for b in banks:
        sets = bank_to_settlement.get(b.id, [])
        if len(sets) == 1:
            sid = sets[0].id
            attached = False
            # Find the chain with this settlement
            for pid, chain in payment_chains.items():
                if chain.settlement and chain.settlement.id == sid:
                    chain.bank = b
                    used_records.add(b.id)
                    chain.evidence.append(Evidence(source="bank_transaction", field="utr", value=b.utr, strength=EvidenceStrength.STRONG))
                    attached = True
                    break
            if not attached:
                # It's an orphan settlement matched to a bank
                c = CandidateChain(settlement=sets[0], bank=b, score=0.99, match_type="EXACT")
                c.evidence.append(Evidence(source="bank_transaction", field="utr", value=b.utr, strength=EvidenceStrength.STRONG))
                orphan_settlement_chains[sid] = c
                used_records.add(sid)
                used_records.add(b.id)

    unmatched = []
    for rlist in [orders, payments, settlements, banks]:
        for r in rlist:
            if r.id not in used_records:
                unmatched.append(r)
                
    return list(payment_chains.values()) + list(orphan_settlement_chains.values()), unmatched
