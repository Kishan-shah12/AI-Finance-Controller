import pytest
from app.services.synthetic.generator import DataGenerator
from app.services.reconciliation.engine import reconcile

def test_1000_record_benchmark():
    gen = DataGenerator(seed=42)
    scenarios = gen.generate(1000)
    
    # Flatten
    all_orders = []
    all_payments = []
    all_settlements = []
    all_banks = []
    for o, p, s, b, gt in scenarios:
        all_orders.extend(o)
        all_payments.extend(p)
        all_settlements.extend(s)
        all_banks.extend(b)
        
    # Build mapping from record ID to scenario_id
    record_to_scenario = {}
    for o_list, p_list, s_list, b_list, gt in scenarios:
        sid = gt.scenario_id
        for r in o_list: record_to_scenario[r.order_id] = sid
        for r in p_list: record_to_scenario[r.payment_id] = sid
        for r in s_list: record_to_scenario[r.settlement_id] = sid
        for r in b_list: record_to_scenario[r.bank_txn_id] = sid
        
    result = reconcile(all_orders, all_payments, all_settlements, all_banks)
    
    metrics = result['metrics']
    processed_source_rows = metrics['records_processed']
    total_source_rows = len(all_orders) + len(all_payments) + len(all_settlements) + len(all_banks)
    
    assert processed_source_rows > 0
    assert processed_source_rows == total_source_rows
    
    # Map results to scenarios
    scenario_decisions = {}
    for r in result['results']:
        # Find scenario_id for this result
        # Just pick the first available ID
        s_id = None
        for rid in r.order_ids + r.payment_ids + r.settlement_ids + r.bank_transaction_ids:
            if rid in record_to_scenario:
                s_id = record_to_scenario[rid]
                break
        
        if s_id:
            # If a scenario has multiple results, we need a priority to roll it up.
            # DUPLICATE_CONFLICT > REVIEW > MATCH_WITH_EXPLAINABLE_VARIANCE > UNRESOLVED > VERIFIED_MATCH
            priority = {
                "DUPLICATE_CONFLICT": 5,
                "REVIEW": 4,
                "UNRESOLVED": 3,
                "MATCH_WITH_EXPLAINABLE_VARIANCE": 2,
                "VERIFIED_MATCH": 1,
                "NONE": 0
            }
            curr = scenario_decisions.get(s_id, "NONE")
            if priority.get(r.decision, 0) > priority.get(curr, 0):
                scenario_decisions[s_id] = r.decision
                
    # Count scenario decisions
    decision_counts = {}
    for dec in scenario_decisions.values():
        decision_counts[dec] = decision_counts.get(dec, 0) + 1
        
    total_scenarios = len(scenarios)
    assert sum(decision_counts.values()) == total_scenarios
    
    print(f"\n--- Benchmark Results ---")
    print(f"Scenarios: {total_scenarios} total")
    for dec, count in decision_counts.items():
        print(f"{count} {dec}")
        
    print(f"\nSource rows: {processed_source_rows} processed")
    print(f"Core Engine Elapsed time: {metrics['elapsed_seconds']:.4f}s")
    print(f"Core Engine Throughput: {metrics['records_per_second']:.2f} records/s (End-to-end not yet measured)")
    
    import json
    with open('scenario_decision_distribution.json', 'w') as f:
        json.dump({
            "total_scenarios": total_scenarios,
            "verified_match": decision_counts.get("VERIFIED_MATCH", 0),
            "explainable_variance": decision_counts.get("MATCH_WITH_EXPLAINABLE_VARIANCE", 0),
            "review": decision_counts.get("REVIEW", 0),
            "unresolved": decision_counts.get("UNRESOLVED", 0),
            "duplicate_conflict": decision_counts.get("DUPLICATE_CONFLICT", 0)
        }, f, indent=2)
        
    with open('source_processing_report.json', 'w') as f:
        json.dump({
            "source_rows": total_source_rows,
            "orders": len(all_orders),
            "payments": len(all_payments),
            "settlements": len(all_settlements),
            "bank_transactions": len(all_banks),
            "rows_processed": processed_source_rows,
            "core_engine_seconds": metrics['elapsed_seconds'],
            "core_engine_rows_per_second": metrics['records_per_second']
        }, f, indent=2)

    
    assert len(result['results']) > 0
