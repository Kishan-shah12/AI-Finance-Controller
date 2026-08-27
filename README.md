# ReconAI: AI Finance Controller

**"Reconcile faster. Explain every variance. Never force a financial match."**

ReconAI is an enterprise-grade reconciliation engine designed for Finance Controllers. It automatically bridges Orders, Payments, Settlements, and Bank Transactions, utilizing an intelligent deterministic rule-engine overlaid with LLM-powered variance explanation.

## Core Tenets
- **Precision First**: Prefers an honest exception over an unsafe automated financial match.
- **Provider Agnostic**: Normalizes external data (e.g. Razorpay, Stripe) into a canonical reconciliation schema.
- **Scientifically Evaluated**: Evaluated against a mathematically isolated synthetic ground-truth dataset ensuring standard and safe-auto-match recall metrics are rigorously truthful.

## Architecture

```text
[ Vercel / Next.js ] -> [ FastAPI on Render ] -> [ Supabase PostgreSQL ]
                                |
                   [ Reconciliation Engine ]
                                |
                 [ Synthetic / Razorpay Data ]
```

## Setup & Local Development

1. **Clone the Repository**
2. **Backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables
Review `.env.example`. Do **not** commit actual secrets.
Backend requires a `DATABASE_URL`. If Supabase is used, populate `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`. Razorpay and LLM keys are entirely optional but required for full Live Data & Agent flows.

## Judge Demo Mode (`/demo`)
The Judge Demo provides a 5-minute presentation-ready experience:
1. Opens with **1,000 synthetic records** injected directly via `seed=42`.
2. Executes reconciliation through the live engine.
3. Showcases the core metrics (Operational Match Rate, Standard Precision).
4. Highlights the highest-priority exceptions.
5. Provides an LLM-driven explanation for *why* a variance occurred safely.

## Evaluation Methodology
See `docs/EVALUATION.md`. The benchmark uses three splits (Development, Validation, Locked Test). The Locked Test set (`test_set.json`) is read-only and deliberately isolated from all application execution to ensure zero data leakage.

## Deployment
- **Frontend**: Designed for Vercel. Map `NEXT_PUBLIC_API_URL` to your Render deployment.
- **Backend**: Designed for Render (`render.yaml` provided). Configures Uvicorn and maps CORS via `ALLOWED_ORIGINS`.

## Limitations
- **Multi-Tenant Security**: While Row Level Security (RLS) is intended on Supabase, the demo assumes a single-tenant environment. Ensure RLS policies are rigorously applied before granting third-party user access.
- **Razorpay Sandbox**: Data ingestion is strictly normalized from Razorpay Test Mode; production Razorpay schemas may drift.
