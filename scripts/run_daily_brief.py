#!/usr/bin/env python3
"""SignalBrief Daily Intelligence Briefing Runner Script.

Executes the daily pipeline, validates editorial quality, outputs run metrics,
and verifies generated HTML and email artifacts.

Supports job lifecycle callbacks to the Cloudflare Worker API when
--job-id and --job-token are provided (set by GitHub Actions workflow_dispatch).
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from signalbrief.pipeline.daily import run_daily_pipeline  # noqa: E402
from signalbrief.pipeline.run_state import PipelineStatus  # noqa: E402


def post_job_callback(
    worker_url: str,
    job_id: str,
    job_token: str,
    status: str,
    metrics: Optional[dict] = None,
) -> None:
    """Send a status callback to the Worker job endpoint. Non-fatal on failure."""
    try:
        import requests

        payload = {"status": status}
        if metrics:
            payload.update(metrics)

        resp = requests.post(
            f"{worker_url.rstrip('/')}/api/jobs/{job_id}/callback",
            json=payload,
            headers={
                "Authorization": f"Bearer {job_token}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        if resp.status_code not in (200, 201):
            print(f"  [callback] WARNING: Worker returned {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        else:
            print(f"  [callback] Job {job_id} -> {status} acknowledged.")
    except Exception as e:  # pragma: no cover
        print(f"  [callback] WARN: Could not reach Worker ({e}). Continuing.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Run SignalBrief Daily Pipeline")
    parser.add_argument("--domain", default="manufacturing", help="Domain to run (default: manufacturing)")
    parser.add_argument("--date", default=None, help="Run date YYYY-MM-DD (default: today)")
    parser.add_argument("--sync", action="store_true", help="Synchronize report with Cloudflare Worker edge API")
    parser.add_argument("--api-url", default=None, help="Cloudflare Worker API base URL")
    parser.add_argument("--api-key", default=None, help="Internal API secret key")
    parser.add_argument("--dispatch-email", action="store_true", help="Dispatch email to subscribers")
    # Job lifecycle args (set by Worker via workflow_dispatch)
    parser.add_argument("--job-id", default=None, help="Pipeline job ID for callback reporting")
    parser.add_argument("--job-token", default=None, help="Pipeline job callback token")
    parser.add_argument("--worker-url", default=None, help="Cloudflare Worker base URL for callbacks")
    args = parser.parse_args()

    # Resolve callback config from args or environment
    job_id = args.job_id or os.getenv("PIPELINE_JOB_ID") or None
    job_token = args.job_token or os.getenv("PIPELINE_JOB_TOKEN") or None
    worker_url = (
        args.worker_url
        or os.getenv("PIPELINE_WORKER_URL")
        or os.getenv("SIGNALBRIEF_API_URL")
        or None
    )
    has_callback = bool(job_id and job_token and worker_url)

    print(f"Executing SignalBrief for domain: {args.domain} (date: {args.date or 'today'}, sync: {args.sync})")
    if has_callback:
        print(f"  Job ID: {job_id} | Worker: {worker_url}")

    state = run_daily_pipeline(
        domain_id=args.domain,
        run_date=args.date,
        sync_cloud=args.sync,
        api_url=args.api_url or worker_url,
        internal_key=args.api_key,
        dispatch_email=args.dispatch_email,
        job_id=job_id,
    )

    if state.status == PipelineStatus.ARCHIVED:
        print("\n==========================================")
        print(" [SUCCESS] SignalBrief Daily Pipeline Run")
        print(f" Run ID:             {state.run_id}")
        print(f" Articles Ingested:  {state.articles_collected}")
        print(f" Articles Analyzed:  {state.articles_processed}")
        print(f" Reports Generated:  {state.reports_generated}")
        print("==========================================\n")

        if has_callback:
            post_job_callback(
                worker_url, job_id, job_token, "completed",
                {
                    "articles_collected": state.articles_collected,
                    "articles_processed": state.articles_processed,
                    "relevant_articles": getattr(state, "relevant_articles", 0),
                    "clusters_formed": getattr(state, "clusters_formed", 0),
                    "report_id": getattr(state, "report_id", None),
                },
            )
        sys.exit(0)
    else:
        print("\n==========================================")
        print(f" [FAILED] Pipeline status: {state.status.value}")
        print(f" Error: {state.error_message}")
        print("==========================================\n", file=sys.stderr)

        if has_callback:
            post_job_callback(
                worker_url, job_id, job_token, "failed",
                {"error_message": state.error_message or "Unknown pipeline failure"},
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
