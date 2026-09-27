# Deployment Workflow

This workflow covers safety gates, environment promotion, and deployment rules for SignalBrief's Cloudflare infrastructure.

## Deployment Stack
- **Frontend**: Cloudflare Pages (Astro + React static site)
- **Backend API & Scheduler**: Cloudflare Workers
- **Database**: Cloudflare D1 (SQLite-compatible distributed relational database)
- **Storage**: Cloudflare R2 (Private S3-compatible bucket for HTML reports)
- **Email Delivery**: Gmail SMTP / worker transport (10 invited users max)

## Safety Checklist Before Deployment

1. **Pre-flight verification**:
   - All pytest unit and integration tests pass (`pytest`).
   - Notebook reproducibility runs cleanly from top to bottom.
   - Database migrations in `migrations/` are forward-compatible and tested locally with `wrangler d1 execute --local`.

2. **Secrets & Quotas**:
   - No hardcoded API keys or credentials in repository files.
   - Cloudflare secrets configured via `wrangler secret put`.
   - Free-tier limits verified:
     - Cloudflare Workers: 100,000 requests/day
     - Cloudflare D1: 5M reads/day, 100k writes/day, 5 GB storage
     - Cloudflare R2: 10 GB storage, 1M Class A operations/month, 10M Class B operations/month
     - Gmail SMTP: maximum 500 emails/day (SignalBrief targets 10 subscribers)

3. **Idempotency & Failure Recovery**:
   - Running the scheduled worker multiple times in the same day will update or skip existing report records, never generate duplicate emails.
   - Failed email attempts are logged in `email_logs` table with backoff retry tracking.
