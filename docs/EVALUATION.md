# ReconAI Evaluation Methodology

This document outlines the evaluation architecture and methodology for the Phase 6 Locked Test Evaluation.

## 1. Dataset Methodology
The dataset is synthetically generated via the internal DataGenerator and split into `dev`, `val`, and `test` files.
- **Dev (70%)**: Used for training the ML Scorer.
- **Val (15%)**: Used for threshold tuning, calibration, and policy searching.
- **Test (15%)**: Read-only **Locked Test** set. Only touched for the final once-per-version evaluation.

## 2. Feature Set
- `id_similarity`
- `amount_similarity`
- `date_proximity`
- `description_similarity`
- `fee_consistency`
- `tax_consistency`
- `customer_relationship`
- `merchant_relationship`
- `payment_method_consistency`
- `settlement_timing_consistency`

## 3. Model Training & Comparison
The `TrainedLogisticScorer` utilizes Scikit-Learn's `LogisticRegression`. Features are extracted deterministically for ambiguous candidates and fitted against Ground Truth.
- **Comparison**: The Trained Scorer achieved `1.0000` F1 on the Validation set alongside the Baseline deterministic Scorer. 
- **Freeze**: The trained model version is logged in `evaluation_config.json`.

## 4. Threshold Tuning & Ambiguity Margin
Thresholds were tuned on the **Validation Set** over a grid search aiming to maximize F1 while keeping False-Match rates extremely low (safeguarding the principle of safe automation).
- Best Ambiguity Margin: `0.02`
- Best Auto-Match Threshold: `0.80`
- Best Review Threshold: `0.40`

## 5. Model Freeze Process
Configuration values are dumped to `evaluation/final/evaluation_config.json`. This exact frozen state is utilized for the single, final Locked Test pass.

## 6. Metric Definitions
### Standard ML Metrics
- **Standard Precision**: `Correct Auto-Matches / All Predicted Auto-Matches`
- **Overall Match Recall**: `Correct Auto-Matches / All Ground-Truth True Matches`
- **Standard F1**: `2 * Standard Precision * Overall Match Recall / (Standard Precision + Overall Match Recall)`
- **False-Match Rate**: `Incorrect Auto-Matches / All Predicted Auto-Matches`

### Operational Metrics (Business Focus)
- **Operational Match Rate**: `(VERIFIED_MATCH + MATCH_WITH_EXPLAINABLE_VARIANCE) / TOTAL_SCENARIOS`
- **Strict Verified Match Rate**: `VERIFIED_MATCH / TOTAL_SCENARIOS`
- **Auto-Match Rate**: `(VERIFIED_MATCH + MATCH_WITH_EXPLAINABLE_VARIANCE) / TOTAL_SCENARIOS`
- **Review Rate**: `REVIEW scenarios / TOTAL_SCENARIOS`
- **Exception Rate**: `(UNRESOLVED + DUPLICATE_CONFLICT) / TOTAL_SCENARIOS`

### Custom Safe-Automation Metrics
- **Safe Auto-Match Precision**: Same as standard precision.
- **Safe Auto-Match Recall**: `Correct Auto-Matches / Safely Auto-Matchable Scenarios` (Excludes partials/ambiguous ground-truths that the policy correctly dictates should NOT be auto-matched).

## 6.5 Locked Test Methodology
The locked test set is strictly read-only during the final evaluation phase.
**IMPORTANT: The locked test set was not used to tune the model, features, thresholds, or ambiguity margin.**

## 6.6 Threshold Sensitivity Methodology
Threshold sensitivity analysis is performed exclusively on the Validation dataset. It grid-searches combinations of the Auto-Match threshold and Review threshold, computing Standard F1 and False-Match Rate. The goal is to maximize useful automation while strictly bounding the False-Match Rate near 0%.

## 7. Exception Methodology
All exceptions (Unresolved, Review, Duplicates) are exported explicitly to `exception_report.json`. No difficult scenario is hidden; the raw confidence, explanation payload, and exception types are surfaced directly to the user interface.

## 8. Limitations
- **Synthetic Distribution**: This evaluation operates entirely on synthetic data. Real production variance distributions (and multi-gateway schemas) will degrade raw F1 scores and require robust re-tuning.
- **End-to-End Throughput**: Currently, only the Core Engine in-memory computational throughput is measured. Full I/O database latency mapping has not been benchmarked.

## 9. Reproducibility Procedure
Run the following script to reproduce the metrics perfectly:
```bash
python -m app.services.evaluation.evaluate
```
This guarantees identical decision distributions against the static, isolated ground truth test files.
