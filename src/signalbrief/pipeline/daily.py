"""Daily pipeline execution orchestrator (CLI entrypoint)."""

import argparse
import sys
from datetime import date

from signalbrief.config.loader import load_domain_config, load_pipeline_config
from signalbrief.pipeline.run_state import PipelineStatus, RunState


def run_daily_pipeline(domain_id: str = "manufacturing", run_date: str = None) -> RunState:
    """Execute the daily pipeline stages in order."""
    target_date = run_date or date.today().isoformat()
    state = RunState(
        run_id=f"run_{domain_id}_{target_date}",
        domain_id=domain_id,
        run_date=target_date,
    )

    print(f"Starting SignalBrief daily pipeline for '{domain_id}' on {target_date}...")
    pipeline_cfg = load_pipeline_config()
    domain_cfg = load_domain_config(domain_id)

    # In Phase 0 & Phase 1, the pipeline logic is developed and validated via Notebooks 00-10.
    # Phase 2 integrates the full pipeline execution here.
    state.transition_to(PipelineStatus.COLLECTING)
    print(f"Loaded '{pipeline_cfg.name}' for domain '{domain_cfg.name}' successfully.")
    state.transition_to(PipelineStatus.ARCHIVED)
    return state


def main():
    parser = argparse.ArgumentParser(description="SignalBrief Daily Pipeline Runner")
    parser.add_argument("--domain", default="manufacturing", help="Domain ID (default: manufacturing)")
    parser.add_argument("--date", default=None, help="Run date YYYY-MM-DD")
    args = parser.parse_args()

    state = run_daily_pipeline(domain_id=args.domain, run_date=args.date)
    print(f"Pipeline status: {state.status.value}")
    if state.error_message:
        print(f"Error: {state.error_message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
