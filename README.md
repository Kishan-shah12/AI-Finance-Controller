# ReconAI: AI Finance Controller

**"Reconcile faster. Explain every variance. Never force a financial match."**

ReconAI is an enterprise-grade reconciliation engine designed for Finance Controllers. It automatically bridges Orders, Payments, Settlements, and Bank Transactions, utilizing an intelligent deterministic rule-engine overlaid with AI variance explanation.

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
   python3.13 -m venv .venv
   source .venv/bin/activate
   python -m pip install -e ".[dev]"
   ```
3. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables
Review `.env.example`. Do **not** commit actual secrets.
Backend requires a `DATABASE_URL`. If Supabase is used, populate `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.

## Deployment Modes

- **LOCAL DEVELOPMENT**: Runs entirely locally using SQLite or local Postgres. Frontend runs on `localhost:3000`, backend on `localhost:8000`.
- **DEMO MODE**: A single-tenant demonstration mode using deterministic synthetic data (SyntheticProvider). Designed to showcase capabilities safely without exposing production data.
- **RAZORPAY TEST MODE**: A provider interoperability feature. Ingests data from Razorpay's sandbox/test mode to demonstrate API connectivity and normalization.
- **PRODUCTION DEPLOYMENT**: Designed for Render (Backend) and Vercel (Frontend). Requires secure PostgreSQL (e.g., Supabase) with strict Row Level Security (RLS) enforcement.

*Note: If the demo environment is expected to ship with Gemini configured, this must be set up separately as a deployment requirement via `GEMINI_API_KEY`.*

## Judge Demo Mode (`/demo`)
The Judge Demo provides a 5-minute presentation-ready experience:
1. Opens with **1,000 synthetic records** injected directly via `seed=42` (deterministic SyntheticProvider mode).
2. Executes reconciliation through the live engine.
3. Showcases the core metrics (Operational Match Rate, Standard Precision).
4. Highlights the highest-priority exceptions.
5. The Judge Demo provides an evidence-backed AI explanation when an LLM provider is configured.

## Performance
- **Core Engine Throughput**: ~99K records/sec local in-memory benchmark.
- **Local E2E API latency**: measured on localhost.
*(Note: These are local benchmark metrics and do not represent production performance).*

## Security & Evaluation
- **Synthetic Data**: Synthetic data is used exclusively for evaluation.
- **Test Isolation**: The locked test answer key (`test_set.json`) is read-only and strictly isolated from all application execution to prevent data leakage.
- **Single-Tenant Demo**: The current demo is single-tenant. 
- **Production RLS**: Supabase RLS (Row Level Security) requires production configuration and enforcement before granting any third-party user access.

## Limitations
- **Razorpay Sandbox**: Data ingestion is strictly normalized from Razorpay Test Mode; production Razorpay schemas may drift.
