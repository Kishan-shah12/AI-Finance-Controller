# Razorpay Test Mode Integration

Razorpay Test Mode integration validates provider interoperability. It is not used as the source of the locked benchmark.

## 1. Provider Architecture
The application uses a `PaymentProvider` interface to abstract data ingestion. The `RazorpayProvider` fetches live test data, normalizes it into canonical shapes, and feeds it into the reconciliation engine.

## 2. Required Credentials & Environment Variables
- `RAZORPAY_KEY_ID`: Server-side API Key ID.
- `RAZORPAY_KEY_SECRET`: Server-side API Key Secret.

These credentials MUST be kept strictly on the server and are never exposed via APIs or logs.

## 3. Supported APIs & Canonical Mapping
1. **GET /v1/settlements**: Maps to canonical `Settlement`.
2. **GET /v1/settlements/recon/combined**: Used to find transactions mapping payment_id/order_id to settlement_id.
3. **GET /v1/payments/{id}**: Fetches missing payment details (amount, method) not available in settlement recon alone.
4. **GET /v1/orders/{id}**: Fetches order-level details.

*Note: All amounts fetched from Razorpay are in the smallest currency unit (e.g., paise) and are safely converted to `Decimal` INR before injection.*

## 4. Error Handling & Retry Policy
- Bounded retries are used for network timeouts and `429 Too Many Requests`.
- `401`/`403` and `404` errors are terminal and will NOT be retried.

## 5. Security
- Secrets are NEVER logged.
- The `Provider Status` endpoint only returns a boolean `configured` flag without echoing any part of the keys.

## 6. Demo Protection
- Judge Demo Mode remains purely synthetic and deterministic (Seed 42).
- You cannot select the Razorpay provider in the Judge Demo flow.
