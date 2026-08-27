# ReconAI Reconciliation Engine

## Architecture

The ReconAI reconciliation engine operates completely deterministically, isolating production data from evaluation ground-truth.

### 1. Normalization (Stage 0)
Raw records (Orders, Payments, Settlements, Bank Transactions) are normalized into a unified `NormalizedRecord` format. This aligns fields like amounts (to `Decimal`), dates (to timestamps), and IDs for consistent comparison.

### 2. Exact Matching (Stage 1)
Finds links based on explicit identifiers:
- `order_id` in payment
- `payment_id` in settlement
- `utr` in bank transactions
Chains formed here receive a confidence of `0.99`.

### 3. Candidate Generation (Stage 2)
For unmatched records, rule-based logic generates candidates using indexed grouping (e.g., grouped by `merchant_id` and amount, filtered by a 5-day window). This avoids naive O(N²) comparisons across the dataset, guaranteeing high throughput.

### 4. Fuzzy / ML Scoring (Stage 3)
An initial Scikit-Learn Logistic Regression model scores candidates based on feature vectors like `id_similarity`, `amount_similarity`, and `date_proximity`. It translates the feature set into a deterministic `confidence` probability (0.0 to 1.0).

**Scoring Model Status**: 
The current scorer is explicitly named the **"Deterministic Logistic-Style Baseline"**. It is NOT a trained ML model. It uses manually specified weights to simulate a trained `LogisticRegression` model without importing ground truth or requiring a `.pkl` file. This ensures Phase 5 remains fully deterministic and explainable, while keeping the architecture compatible with a true trained ML model for Phase 6.

### 5. Variance Analysis
Analyzes mathematical relationships, verifying `net = gross - fee - tax`. Detects explainable conditions (like `FEE_VARIANCE` or `PARTIAL_SETTLEMENT`) by checking numeric consistency, as well as checking `UTR_MISMATCH`.

**Explainable Variance Definition**: 
A standard expected fee deduction (e.g. 2% + 1.50) is NOT an explainable variance; it is standard operating procedure and results in `VERIFIED_MATCH`. `MATCH_WITH_EXPLAINABLE_VARIANCE` is strictly reserved for scenarios where there is an additional discrepancy that can be explicitly explained using evidence (e.g., unusual fee, additional adjustment, documented timing difference).

### 6. Decision Engine & Ambiguity Handling
Classifies the candidate chain into one of five decisions:
- `VERIFIED_MATCH`: High confidence, all expected relationships are satisfied (including standard expected fees).
- `MATCH_WITH_EXPLAINABLE_VARIANCE`: High confidence, but possesses an additional explainable variance (e.g. unexpected fee).
- `REVIEW`: Ambiguous margin (multiple candidates with scores within 0.05), or moderate confidence.
- `UNRESOLVED`: Low confidence, missing records.
- `DUPLICATE_CONFLICT`: Conflicting duplicates found.

### Evidence Generation
Each generated `ReconciliationResult` includes an `evidence` array pinpointing exactly why a decision was reached, fulfilling the core principle of explainability.

## Terminology and Metrics

**Scenario-level vs Source-row terminology**:
- **Scenario**: A full logical business lifecycle involving an order, payment, settlement, and bank transaction (or variations thereof). There are ~1,000 scenarios generated.
- **Source rows**: The individual raw records (Orders, Payments, Settlements, Bank Transactions). There are ~3,992 source rows processed.
Reporting must strictly distinguish between these two units to maintain mathematical consistency.

## Throughput Strategy
The engine utilizes `O(N)` grouping with dictionaries and sets for exact matching and rule-based candidate generation, scaling safely to tens of thousands of records without significant performance degradation.

**Core vs End-to-End Throughput**:
- **Core Engine Throughput**: Measures the in-memory processing speed of the reconciliation engine itself (e.g., ~99,000 records/sec).
- **End-to-End Throughput**: Includes data loading, normalization, matching, decision logic, database inserts, and API latency. *This is not yet measured in Phase 5.*

## Limitations
- Explainable variance logic for fees/taxes is currently bound to the synthetic generator's specific formula. In production, this would dynamically reference merchant-specific contract configurations.
