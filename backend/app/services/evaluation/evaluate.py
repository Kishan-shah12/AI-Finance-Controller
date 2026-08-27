import os
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from app.services.evaluation.dataset import load_split
from app.services.reconciliation.engine import reconcile
from app.services.reconciliation.thresholds import ReconciliationThresholds
from app.services.evaluation.model import TrainedLogisticScorer
from app.services.reconciliation.normalization import normalize_order, normalize_payment, normalize_settlement, normalize_bank
from app.services.reconciliation.stage1_exact import run_stage1_exact
from app.services.reconciliation.stage2_rules import run_stage2_rules

def extract_training_chains(orders, payments, settlements, banks):
    norm_orders = [normalize_order(o) for o in orders]
    norm_payments = [normalize_payment(p) for p in payments]
    norm_settlements = [normalize_settlement(s) for s in settlements]
    norm_banks = [normalize_bank(b) for b in banks]
    exact_chains, unmatched = run_stage1_exact(norm_orders, norm_payments, norm_settlements, norm_banks)
    rule_chains, _ = run_stage2_rules(unmatched, exact_chains)
    return exact_chains + rule_chains

def evaluate_predictions(results, gt_list):
    # Create record_to_scenario map
    record_to_scenario = {}
    gt_map = {gt.scenario_id: gt for gt in gt_list}
    for gt in gt_list:
        if gt.order_id: record_to_scenario[gt.order_id] = gt.scenario_id
        if gt.payment_id: record_to_scenario[gt.payment_id] = gt.scenario_id
        if gt.settlement_id: record_to_scenario[gt.settlement_id] = gt.scenario_id
        if gt.bank_transaction_id: record_to_scenario[gt.bank_transaction_id] = gt.scenario_id
        
    scenario_decisions = {}
    for r in results:
        s_id = None
        for rid in r.order_ids + r.payment_ids + r.settlement_ids + r.bank_transaction_ids:
            if rid in record_to_scenario:
                s_id = record_to_scenario[rid]
                break
        
        if s_id:
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
                
    total_scenarios = len(gt_list)
    auto_matched = sum(1 for d in scenario_decisions.values() if d in ["VERIFIED_MATCH", "MATCH_WITH_EXPLAINABLE_VARIANCE"])
    review = sum(1 for d in scenario_decisions.values() if d == "REVIEW")
    unresolved = sum(1 for d in scenario_decisions.values() if d in ["UNRESOLVED", "DUPLICATE_CONFLICT"])
    
    # Calculate precision / recall
    correct_auto_matches = 0
    incorrect_auto_matches = 0
    
    # Standard Denominator: ALL true ground-truth relationships
    all_true_matches = sum(1 for gt in gt_list if gt.ground_truth_match)
    
    # Custom Denominator: Only those that are SAFELY auto-matchable based on our policy
    safely_auto_matchable = sum(1 for gt in gt_list if gt.ground_truth_match and gt.expected_decision in ["VERIFIED_MATCH", "MATCH_WITH_EXPLAINABLE_VARIANCE"])
    
    for s_id, dec in scenario_decisions.items():
        if dec in ["VERIFIED_MATCH", "MATCH_WITH_EXPLAINABLE_VARIANCE"]:
            gt = gt_map[s_id]
            if gt.ground_truth_match:
                correct_auto_matches += 1
            else:
                incorrect_auto_matches += 1
                
    standard_precision = correct_auto_matches / auto_matched if auto_matched > 0 else 0.0
    safe_auto_match_precision = standard_precision
    
    overall_match_recall = correct_auto_matches / all_true_matches if all_true_matches > 0 else 0.0
    safe_auto_match_recall = correct_auto_matches / safely_auto_matchable if safely_auto_matchable > 0 else 0.0
    
    standard_f1 = 2 * standard_precision * overall_match_recall / (standard_precision + overall_match_recall) if standard_precision + overall_match_recall > 0 else 0.0
    
    false_match_rate = incorrect_auto_matches / auto_matched if auto_matched > 0 else 0.0
    
    return {
        "total_scenarios": total_scenarios,
        "operational_match_rate": auto_matched / total_scenarios,
        "strict_verified_match_rate": sum(1 for d in scenario_decisions.values() if d == "VERIFIED_MATCH") / total_scenarios,
        "auto_match_rate": auto_matched / total_scenarios,
        
        "standard_precision": standard_precision,
        "overall_match_recall": overall_match_recall,
        "standard_f1": standard_f1,
        
        "safe_auto_match_precision": safe_auto_match_precision,
        "safe_auto_match_recall": safe_auto_match_recall,
        
        "false_match_rate": false_match_rate,
        "review_rate": review / total_scenarios,
        "exception_rate": unresolved / total_scenarios,
        "decisions": scenario_decisions
    }

def main():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    base_path = root_dir / 'data'
    eval_dir = root_dir / 'backend' / 'evaluation' / 'final'
    eval_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Datasets
    print("Loading datasets...")
    dev_o, dev_p, dev_s, dev_b, dev_gt = load_split('dev', base_path)
    val_o, val_p, val_s, val_b, val_gt = load_split('val', base_path)
    test_o, test_p, test_s, test_b, test_gt = load_split('test', base_path)
    
    # 2. Train Model
    print("Extracting features from dev set...")
    dev_chains = extract_training_chains(dev_o, dev_p, dev_s, dev_b)
    gt_map = {gt.scenario_id: gt for gt in dev_gt}
    
    print("Training LogisticScorer...")
    scorer = TrainedLogisticScorer()
    scorer.train(dev_chains, gt_map)
    
    # 3. Model Comparison
    print("Evaluating baseline on Val...")
    res_base = reconcile(val_o, val_p, val_s, val_b)
    met_base = evaluate_predictions(res_base['results'], val_gt)
    
    print("Evaluating trained model on Val...")
    res_trained = reconcile(val_o, val_p, val_s, val_b, scorer=scorer)
    met_trained = evaluate_predictions(res_trained['results'], val_gt)
    
    print(f"Baseline F1: {met_base['standard_f1']:.4f}")
    print(f"Trained F1: {met_trained['standard_f1']:.4f}")
    
    # 4. Threshold Sensitivity on Val Set
    print("Running threshold sensitivity on Val set...")
    best_f1 = 0
    best_thresh = ReconciliationThresholds()
    
    val_dir = root_dir / 'backend' / 'evaluation' / 'validation'
    val_dir.mkdir(parents=True, exist_ok=True)
    
    sensitivity_results = []
    
    for auto_m in [0.70, 0.75, 0.80, 0.85, 0.90]:
        # Keep review threshold logic consistent
        review_m = 0.40
        if review_m >= auto_m:
            review_m = auto_m - 0.10
        ambig = 0.02
        
        tc = ReconciliationThresholds(verified_match_min=0.95, explainable_variance_min=auto_m, review_min=review_m, ambiguity_margin=ambig)
        res = reconcile(val_o, val_p, val_s, val_b, scorer=scorer, thresholds=tc)
        met = evaluate_predictions(res['results'], val_gt)
        
        sensitivity_results.append({
            "auto_match_threshold": auto_m,
            "review_threshold": review_m,
            "standard_precision": met['standard_precision'],
            "overall_match_recall": met['overall_match_recall'],
            "standard_f1": met['standard_f1'],
            "false_match_rate": met['false_match_rate'],
            "auto_match_rate": met['auto_match_rate'],
            "review_rate": met['review_rate'],
            "exception_rate": met['exception_rate']
        })
        
        if met['standard_f1'] > best_f1 and met['false_match_rate'] < 0.05:
            best_f1 = met['standard_f1']
            best_thresh = tc
            
    # Save sensitivity results
    with open(val_dir / 'threshold_sensitivity.json', 'w') as f:
        json.dump(sensitivity_results, f, indent=2)
        
    with open(val_dir / 'threshold_sensitivity.csv', 'w') as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=sensitivity_results[0].keys())
        writer.writeheader()
        writer.writerows(sensitivity_results)
                    
    # The instructions specify we MUST freeze: auto_match_threshold = 0.80, review_min = 0.40, ambiguity_margin = 0.02
    # So regardless of best_thresh, we freeze the provided explicit configuration.
    frozen_thresh = ReconciliationThresholds(verified_match_min=0.95, explainable_variance_min=0.80, review_min=0.40, ambiguity_margin=0.02)
    
    if frozen_thresh.explainable_variance_min != best_thresh.explainable_variance_min:
        print(f"CURRENT FROZEN CONFIGURATION: Auto={frozen_thresh.explainable_variance_min}")
        print(f"RECOMMENDED ALTERNATIVE: Auto={best_thresh.explainable_variance_min}")
    else:
        print(f"CURRENT FROZEN CONFIGURATION IS RECOMMENDED: Auto={frozen_thresh.explainable_variance_min}")
    
    # 5. Lock Config
    scorer.save_config(eval_dir / 'evaluation_config.json', {
        "verified_match_min": frozen_thresh.verified_match_min,
        "explainable_variance_min": frozen_thresh.explainable_variance_min,
        "review_min": frozen_thresh.review_min,
        "ambiguity_margin": frozen_thresh.ambiguity_margin
    })
    
    # 6. Locked Test Evaluation
    print("Running frozen evaluation on Locked Test Set...")
    res_test = reconcile(test_o, test_p, test_s, test_b, scorer=scorer, thresholds=frozen_thresh)
    met_test = evaluate_predictions(res_test['results'], test_gt)
    
    # Generate Output Reports
    with open(eval_dir / 'metrics.json', 'w') as f:
        m = dict(met_test)
        del m['decisions']
        m['core_engine_throughput'] = res_test['metrics']['records_per_second']
        m['end_to_end_throughput'] = "not measured"
        json.dump(m, f, indent=2)
        
    # Decision distribution
    decisions = {}
    for d in met_test['decisions'].values():
        decisions[d] = decisions.get(d, 0) + 1
    with open(eval_dir / 'decision_distribution.json', 'w') as f:
        json.dump(decisions, f, indent=2)
        
    # Exception report
    exceptions = []
    for r in res_test['results']:
        if r.decision in ["REVIEW", "UNRESOLVED", "DUPLICATE_CONFLICT"]:
            exceptions.append({
                "decision": r.decision,
                "exception_type": r.exception_type,
                "confidence": r.confidence,
                "evidence": [e.model_dump() for e in r.evidence],
                "variance_details": r.variance_details
            })
    with open(eval_dir / 'exception_report.json', 'w') as f:
        json.dump(exceptions, f, indent=2)
        
    # Markdown summary
    summary = f"""# Final Evaluation Summary

These metrics were measured on a locked synthetic test set and were not used for model or threshold tuning.
The dataset is synthetic and designed for hackathon evaluation.

### Model & Configuration
- **Model Version**: {scorer.model_version}
- **Auto-Match Threshold**: {frozen_thresh.explainable_variance_min}
- **Review Threshold**: {frozen_thresh.review_min}
- **Ambiguity Margin**: {frozen_thresh.ambiguity_margin}

### Standard ML Metrics
- **Standard Precision**: {met_test['standard_precision']:.2%}
- **Overall Match Recall**: {met_test['overall_match_recall']:.2%}
- **Standard F1 Score**: {met_test['standard_f1']:.2%}
- **False-Match Rate**: {met_test['false_match_rate']:.2%}

### Operational Metrics (Business Focus)
- **Operational Match Rate**: {met_test['operational_match_rate']:.2%}
- **Strict Verified Match Rate**: {met_test['strict_verified_match_rate']:.2%}
- **Auto-Match Rate**: {met_test['auto_match_rate']:.2%}
- **Review Rate**: {met_test['review_rate']:.2%}
- **Exception Rate**: {met_test['exception_rate']:.2%}

### Custom Safe-Automation Metrics
- **Auto-Match Precision**: {met_test['safe_auto_match_precision']:.2%} (same as standard precision)
- **Safe Auto-Match Recall**: {met_test['safe_auto_match_recall']:.2%} (Denominator restricted to safely auto-matchable scenarios)

### Throughput
- **Core Engine**: {res_test['metrics']['records_per_second']:.2f} records/s
- **End-to-End**: not measured
"""
    with open(eval_dir / 'evaluation_summary.md', 'w') as f:
        f.write(summary)
        
    print("Evaluation completed successfully.")

if __name__ == "__main__":
    main()
