# Security and Responsible Use

This document outlines the security posture, authentication protocols, and responsible AI limitations of ReconAI.

## 1. Secret Handling
ReconAI is architected such that all third-party secrets (Supabase, Razorpay, LLM API Keys) remain strictly server-side.
- The `RAZORPAY_KEY_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`, and LLM keys are never exposed in NextJS frontend bundles or public repositories.
- Backend API responses carefully filter and normalize data; exceptions redact raw provider API error strings to prevent credentials leakage.
- Logs strictly avoid dumping un-sanitized environments.

## 2. Authentication and Authorization
In a production deployment, ReconAI connects to Supabase PostgreSQL.
- **Supabase RLS (Row Level Security)** is required for production-grade tenant isolation.
- Currently, RLS verification is an administrative prerequisite. **Limitation**: The initial deployment configuration assumes a single-tenant operations mode unless specific Supabase RLS tenant IDs are actively injected via JWT claims into the backend FastAPI header layer.

## 3. Ground-Truth Protection
To maintain the integrity of the evaluation benchmark, the `test_set.json` representing locked synthetic answers is entirely isolated from the frontend and API layers. The AI Finance Controller Agent is structurally blocked from accessing or inspecting this answer key, ensuring zero-shot honesty.

## 4. API Validation and CORS
- CORS is strictly bound using `ALLOWED_ORIGINS` to prevent cross-site request forgery.
- All incoming requests are marshaled through Pydantic schemas validating payload integrity and mitigating injection vectors.

## 5. Audit Logging
Every mutable action taken (running reconciliation, modifying exception states, escalating, linking providers) emits an immutable `AuditEvent` natively tied to the user/actor and linked temporally to the exact reconciliation batch ID. 

## 6. Provider Security
- **Razorpay**: Operates exclusively in Test Mode. The backend executes bounded retries and logs exceptions minimally without printing auth scopes.
- **Synthetic**: Safe by default as records exist purely in-memory before PostgreSQL persistence.
