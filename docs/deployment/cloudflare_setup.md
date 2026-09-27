# Cloudflare Setup & Free Tier Guide

SignalBrief is architected to operate comfortably within Cloudflare's generous free tier.

## Required Cloudflare Services

1. **Cloudflare D1 (Database)**
   - Create database: `wrangler d1 create signalbrief-d1`
   - Apply migrations: `wrangler d1 execute signalbrief-d1 --file=./migrations/0001_initial_schema.sql`
2. **Cloudflare R2 (Object Storage)**
   - Create bucket: `wrangler r2 bucket create signalbrief-reports`
3. **Cloudflare Workers (Compute & Scheduler)**
   - Configure secrets:
     ```bash
     wrangler secret put GMAIL_APP_PASSWORD
     wrangler secret put GMAIL_USER
     ```
   - Deploy: `wrangler deploy`
4. **Cloudflare Pages (Frontend)**
   - Connect GitHub repo and deploy `web/` using Astro build preset.
