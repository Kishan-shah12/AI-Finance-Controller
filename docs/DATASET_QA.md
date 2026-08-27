# ReconAI Dataset QA Report

## Overview
This QA report validates the data generation engine prior to Phase 5. All validation checks have passed.

## Generator Execution Metrics
- **Total Scenarios Configured:** 1,000
- **Seed Used:** 42

## Split Distribution
- **Development (70%):** 700 scenarios
- **Validation (15%):** 150 scenarios
- **Test (15%):** 150 scenarios
- **Scenario overlap:** Zero (Scenarios stay entirely within their designated split).

## Scenario Record Distribution (Seed 42)
*Note: Scenarios map slightly higher in record counts (e.g. DUPLICATE generates 2 payments, AMBIGUOUS generates 2 orders/payments).*
- EXACT_MATCH: ~55%
- FEE_VARIANCE: ~8%
- TAX_VARIANCE: ~5%
- MISSING_SETTLEMENT: ~6%
- MISSING_BANK_ENTRY: ~5%
- DUPLICATE: ~5%
- UTR_MISMATCH: ~5%
- PARTIAL_SETTLEMENT: ~5%
- AMBIGUOUS: ~6%

## Validation Checks Passed

### 1. Ambiguous Case Validation
- **Status:** PASS
- **Details:** The `AMBIGUOUS` scenario has been hardened. It now creates two distinct orders and payments belonging to different customer contexts but occurring closely in time. Only one settlement exists, which strips uniquely identifying UTRs, making it genuinely ambiguous which payment it belongs to. Expected classification correctly set to `REVIEW`.

### 2. Reproducibility & Determinism
- **Status:** PASS
- **Details:** Execution of `python -m app.services.synthetic.generator --size 1000 --seed 42` repeatedly yields byte-for-byte identical datasets. Running with `--seed 43` yields a completely distinct dataset.

### 3. Financial Arithmetic
- **Status:** PASS
- **Details:** The relation `net_amount = gross_amount - fee - tax` holds strictly true across all settlement records. For `PARTIAL_SETTLEMENT`, the gross, fee, and tax are all consistently halved so the internal arithmetic remains valid, while the overall settlement amount correctly falls short of the initial payment amount.

### 4. Ground-Truth Isolation
- **Status:** PASS
- **Details:** Ground truth is strictly segregated into `data/ground_truth/`. No production code in the reconciliation engine (Phase 5) will import these files. The `.gitignore` at the project root ensures the locked `test_set.json` remains out of source control.

### 5. Automated Tests
- **Status:** PASS
- **Details:** `pytest tests/unit/test_synthetic.py` executed successfully. 9/9 tests passed, validating deterministic output, arithmetic, date ordering, and all specific exception scenarios.
