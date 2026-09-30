# SignalBrief Deployment & Operations Guide

This guide describes how to configure, test, and deploy SignalBrief across local development and Cloudflare production environments.

---

## 1. Architecture Overview

SignalBrief operates on a hybrid architecture designed for zero cloud execution cost:
- **Intelligence Engine**: Python 3.12 analytics pipeline (`signalbrief`) executed on a scheduled runner (GitHub Actions at 02:00 UTC) or local machine.
- **Edge API & Scheduler**: Cloudflare Worker (`workers/index.js`) providing high-speed REST endpoints, cron handlers, and queues.
- **Metadata Storage**: Cloudflare D1 (serverless SQLite) storing users, preferences, report index, developments, citations, and delivery logs.
- **Report Archive**: Cloudflare R2 object storage holding generated standalone HTML5 reports (`reports/YYYY/MM/DD/report-id.html`).
- **Dashboard**: Astro 4 + TailwindCSS + React 18 web dashboard deployed to Cloudflare Pages.
- **Email Delivery**: Resend API integration (or MailChannels) adhering strictly to the 10-subscriber pilot limit.

---

## 2. Environment Variables & Secrets Reference

| Variable | Environment | Required | Purpose |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Worker / Pipeline | Yes | Environment mode (`development` or `production`). |
| `DEFAULT_DOMAIN` | Worker / Pipeline | Yes | Default domain (default: `manufacturing`). |
| `REPORT_RECIPIENT_LIMIT` | Worker | Yes | Maximum active subscribers permitted (default: `10`). |
| `SIGNALBRIEF_INTERNAL_KEY` | Worker & Runner | Yes | Bearer secret protecting `POST /api/internal/report`. |
| `SIGNALBRIEF_API_URL` | Runner | Yes | Base URL of the Worker API (e.g. `https://signalbrief-worker.workers.dev`). |
| `RESEND_API_KEY` | Worker | Optional | API token for Resend outbound email dispatch. |
| `SENDER_EMAIL` | Worker | Optional | Verified sender address (e.g. `briefs@yourdomain.com`). |
| `CLOUDFLARE_API_TOKEN` | GitHub Secrets | For CI/CD | Token with Workers, D1, R2, and Pages deploy permissions. |
| `CLOUDFLARE_ACCOUNT_ID` | GitHub Secrets | For CI/CD | Cloudflare Account ID. |

---

## 3. Local Development & Testing

### 3.1 Local Python Pipeline
```bash
# 1. Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# 2. Run unit and integration tests
pytest -v

# 3. Run the daily briefing pipeline locally (offline mode)
python scripts/run_daily_brief.py --domain manufacturing

# 4. Artifacts are generated in:
#    reports/generated/daily_brief_manufacturing_YYYY-MM-DD.html
#    reports/previews/daily_email_manufacturing_YYYY-MM-DD.html
```

### 3.2 Local Cloudflare Worker & D1
```bash
# 1. Apply D1 schema migrations locally
npx wrangler d1 migrations apply DB --local

# 2. Verify tables created in local SQLite database
npx wrangler d1 execute DB --local --command "SELECT name FROM sqlite_master WHERE type='table'"

# 3. Run Worker integration test suite
node --test tests/workers/test_worker_api.js

# 4. Start local Worker dev server
npx wrangler dev
# Server will listen on http://localhost:8787
```

### 3.3 Local Web Dashboard
```bash
# 1. Start Astro development server
npm --prefix web run dev
# Dashboard available at http://localhost:4321

# 2. Verify production build
npm --prefix web run build
```

---

## 4. Production Cloudflare Deployment (Gate A / Gate C)

> [!IMPORTANT]
> **Approval Gate A**: Do not execute remote resource creation commands without explicit user authorization.

### 4.1 Cloudflare D1 Provisioning
```bash
# 1. Create remote D1 database
npx wrangler d1 create signalbrief-d1

# 2. Copy the returned database_id into wrangler.toml:
#    [[d1_databases]]
#    binding = "DB"
#    database_name = "signalbrief-d1"
#    database_id = "<your-database-id>"

# 3. Apply schema migration to remote database
npx wrangler d1 migrations apply DB --remote
```

### 4.2 Cloudflare R2 Bucket Provisioning
```bash
# Create report archive bucket
npx wrangler r2 bucket create signalbrief-reports
```

### 4.3 Cloudflare Worker Deployment
```bash
# 1. Set secret internal key in Cloudflare
npx wrangler secret put SIGNALBRIEF_INTERNAL_KEY

# 2. Set Resend API key (optional for email dispatch)
npx wrangler secret put RESEND_API_KEY

# 3. Deploy Worker
npx wrangler deploy --env production
```

### 4.4 Cloudflare Pages Dashboard Deployment
```bash
# Build static dashboard and deploy to Cloudflare Pages
npm --prefix web run build
npx wrangler pages deploy web/dist --project-name=signalbrief
```

---

## 5. Daily Automation (GitHub Actions)

Daily automated execution is configured in `.github/workflows/daily-pipeline.yml`:
1. Executes every morning at **02:00 UTC** via cron.
2. Runs the full 5-stage Python analytics pipeline on an Ubuntu GitHub Actions runner.
3. Automatically authenticates and pushes the validated HTML report and metadata to the Cloudflare Worker API.
4. Uploads execution artifacts for 14-day archival inspection.

### Setting Repository Secrets
In your GitHub repository under **Settings > Secrets and variables > Actions**, configure:
- `SIGNALBRIEF_API_URL`: Your deployed Worker URL (e.g. `https://signalbrief-worker.workers.dev`).
- `SIGNALBRIEF_INTERNAL_KEY`: Matching the secret configured in Cloudflare.
- `SIGNALBRIEF_DISPATCH_EMAIL`: `true` (when live email dispatch is approved under Gate B).

---

## 6. Rollback Procedure

If a deployed Worker or schema migration encounters an unrecoverable failure:
1. **Worker Rollback**:
   ```bash
   # List recent deployments
   npx wrangler deployments list
   # Rollback to specific deployment ID
   npx wrangler rollback <deployment-id>
   ```
2. **Database Rollback**:
   Restore from Cloudflare D1 automated point-in-time backup:
   ```bash
   npx wrangler d1 backup list signalbrief-d1
   npx wrangler d1 backup restore signalbrief-d1 <backup-id>
   ```
3. **Pipeline Runner**:
   The Python daily runner is fully stateless and idempotent. Re-running the pipeline for the same date overwrites the existing report record in D1 without duplicating entries.
