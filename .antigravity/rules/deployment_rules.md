# Deployment Rules

- Deploy the frontend through Cloudflare Pages.
- Use Workers for server-side APIs.
- Use D1 for relational metadata.
- Use R2 for archived report files.
- Use Cron Triggers for scheduled jobs.
- Use Queues for background processing
  when needed.
- Keep the R2 bucket private.
- Enforce per-user authorization.
- Store secrets using Cloudflare secrets.
- Never commit production credentials.
- Respect free-tier quotas.
- Implement retries and idempotency.
- Do not deploy without tests.
- Require explicit approval before
  production deployment or destructive changes.
