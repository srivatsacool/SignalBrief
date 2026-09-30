#!/usr/bin/env python3
"""SignalBrief Daily Intelligence Briefing Runner Script.

Executes the daily pipeline, validates editorial quality, outputs run metrics,
and verifies generated HTML and email artifacts.
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from signalbrief.pipeline.daily import run_daily_pipeline  # noqa: E402
from signalbrief.pipeline.run_state import PipelineStatus  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Run SignalBrief Daily Pipeline")
    parser.add_argument("--domain", default="manufacturing", help="Domain to run (default: manufacturing)")
    parser.add_argument("--date", default=None, help="Run date YYYY-MM-DD (default: today)")
    parser.add_argument("--sync", action="store_true", help="Synchronize report with Cloudflare Worker edge API")
    parser.add_argument("--api-url", default=None, help="Cloudflare Worker API base URL")
    parser.add_argument("--api-key", default=None, help="Internal API secret key")
    parser.add_argument("--dispatch-email", action="store_true", help="Dispatch email to subscribers")
    args = parser.parse_args()

    print(f"Executing SignalBrief for domain: {args.domain} (date: {args.date or 'today'}, sync: {args.sync})...")
    state = run_daily_pipeline(
        domain_id=args.domain,
        run_date=args.date,
        sync_cloud=args.sync,
        api_url=args.api_url,
        internal_key=args.api_key,
        dispatch_email=args.dispatch_email,
    )

    if state.status == PipelineStatus.ARCHIVED:
        print("\n==========================================")
        print(" [SUCCESS] SignalBrief Daily Pipeline Run")
        print(f" Run ID:             {state.run_id}")
        print(f" Articles Ingested:  {state.articles_collected}")
        print(f" Articles Analyzed:  {state.articles_processed}")
        print(f" Reports Generated:  {state.reports_generated}")
        print("==========================================\n")
        sys.exit(0)
    else:
        print("\n==========================================")
        print(f" [FAILED] Pipeline status: {state.status.value}")
        print(f" Error: {state.error_message}")
        print("==========================================\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
