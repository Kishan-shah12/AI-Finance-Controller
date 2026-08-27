# ReconAI Data Generation

## Dataset Purpose
The dataset is synthetic and designed for hackathon evaluation. It represents a realistic payment lifecycle to test the reconciliation engine's ability to handle perfect matches and realistic discrepancies. **Scenario frequencies do not represent production prevalence.**

## Data Sources
1. **Orders**: Initial customer intent.
2. **Payments**: The payment transaction representing user funds capture.
3. **Settlements**: The payment gateway's settlement, often after deducting fees and taxes.
4. **Bank Transactions**: The actual credit appearing in the merchant's bank account.

## Record Schemas
All source datasets use `NUMERIC` types for money fields (represented as `Decimal` in Python). Binary floating point is never used.

## Scenario Types
- **EXACT_MATCH**: All records exist and align perfectly.
- **FEE_VARIANCE**: The settlement fee differs slightly from standard, altering net amount.
- **TAX_VARIANCE**: The settlement tax differs slightly.
- **MISSING_SETTLEMENT**: Payment exists, but no settlement was received.
- **MISSING_BANK_ENTRY**: Settlement exists, but money never hit the bank.
- **DUPLICATE**: A duplicate payment or settlement is introduced.
- **UTR_MISMATCH**: The UTR in the settlement does not match the bank transaction.
- **PARTIAL_SETTLEMENT**: Settlement amount is substantially less than the payment amount.
- **AMBIGUOUS**: Multiple plausible candidates exist with similar amounts/dates but no definitive identifier.

## Scenario Distributions
For a standard 1,000 record dataset, the approximate distribution is:
- 55% EXACT MATCH
- 8% FEE VARIANCE
- 5% TAX VARIANCE
- 6% MISSING SETTLEMENT
- 5% MISSING BANK ENTRY
- 5% DUPLICATE
- 5% UTR MISMATCH
- 5% PARTIAL SETTLEMENT
- 6% AMBIGUOUS

## Ground Truth Design
Ground truth is created alongside the data generation but strictly isolated. It contains:
- `scenario_id` & `scenario_type`
- `record_status` (MATCHABLE / NON_MATCHABLE)
- `expected_decision` (VERIFIED_MATCH, MATCH_WITH_EXPLAINABLE_VARIANCE, REVIEW, UNRESOLVED, DUPLICATE_CONFLICT)
- `exception_type` (if any)

## Train/Validation/Test Split
The generator creates a deterministic seeded split:
- **70% Development (`dev_set.json`)**
- **15% Validation (`val_set.json`)**
- **15% Locked Test (`test_set.json`)**

## Deterministic Seed
Running `python -m app.services.synthetic.generator --size N --seed S` is guaranteed to produce exactly the same CSVs and ground truth JSONs across runs.

## Isolation Rules
**Production code must NEVER import the ground truth files.**
Specifically, the locked test labels (`data/ground_truth/test_set.json`) must remain fully isolated from the public frontend, production reconciliation engine, and runtime APIs.

## Known Limitations
- Data is entirely synthetic; relationships and names are procedurally generated.
- "Ambiguous" scenarios are simplistic right now (duplicate orders nearby in time). More complex adversarial examples would be needed for a real-world test.
- Tax and fee variance currently assume a naive deviation model.
