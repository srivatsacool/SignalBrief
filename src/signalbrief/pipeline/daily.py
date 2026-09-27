"""Daily pipeline execution orchestrator and CLI entrypoint for SignalBrief."""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

from signalbrief.config.defaults import (
    REPORTS_DIR,
    TEMPLATES_DIR,
)
from signalbrief.config.loader import (
    load_domain_config,
    load_pipeline_config,
    load_sources_for_domain,
)
from signalbrief.pipeline.run_state import PipelineStatus, RunState
from signalbrief.pipeline.stages import (
    stage_analyze,
    stage_cluster_and_rank,
    stage_collect,
    stage_preprocess,
    stage_render,
)
from signalbrief.reporting.validation import validate_report

logger = logging.getLogger("signalbrief")


def run_daily_pipeline(
    domain_id: str = "manufacturing",
    run_date: Optional[str] = None,
    output_dir: Optional[Path] = None,
    preview_dir: Optional[Path] = None,
    cached_clean_articles: Optional[List] = None,
) -> RunState:
    """Execute the full 5-stage daily pipeline end-to-end.

    Stages:
        1. Collection (RSS/API ingestion & canonical deduplication)
        2. Preprocessing (HTML stripping, unicode norm, language & length filter)
        3. Analysis (Subtopic classification, NER, sentiment scoring)
        4. Clustering & Ranking (TF-IDF agglomeration & multi-factor scoring)
        5. Report Generation & Validation (Triadic synthesis, HTML & email rendering)
    """
    target_date = run_date or date.today().isoformat()
    state = RunState(
        run_id=f"run_{domain_id}_{target_date}",
        domain_id=domain_id,
        run_date=target_date,
    )

    out_dir = output_dir or (REPORTS_DIR / "generated")
    prev_dir = preview_dir or (REPORTS_DIR / "previews")
    out_dir.mkdir(parents=True, exist_ok=True)
    prev_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load Configurations
        pipeline_cfg = load_pipeline_config()
        domain_cfg = load_domain_config(domain_id)
        sources = load_sources_for_domain(domain_id)
        active_sources = [s for s in sources if s.active]

        logger.info(f"Loaded {len(active_sources)} active sources for '{domain_id}'.")

        # Stage 1: Collection
        if cached_clean_articles is not None:
            clean_articles = cached_clean_articles
            state.articles_collected = len(clean_articles)
            state.articles_processed = len(clean_articles)
            logger.info(f"Using {len(clean_articles)} cached clean articles.")
        else:
            state.transition_to(PipelineStatus.COLLECTING)
            raw_articles, col_stats = stage_collect(active_sources, pipeline_cfg)
            state.articles_collected = len(raw_articles)
            logger.info(f"Ingested {len(raw_articles)} raw articles ({col_stats}).")

            # Stage 2: Preprocessing
            clean_articles, prep_stats = stage_preprocess(raw_articles, pipeline_cfg)
            state.articles_processed = len(clean_articles)
            logger.info(f"Retained {len(clean_articles)} clean articles ({prep_stats}).")

        if not clean_articles:
            raise ValueError(f"No clean articles available for domain '{domain_id}' on {target_date}.")

        # Stage 3: Analysis
        state.transition_to(PipelineStatus.ANALYSING)
        annotated_articles = stage_analyze(clean_articles)
        logger.info(f"Annotated {len(annotated_articles)} articles with NLP attributes.")

        # Stage 4: Clustering & Ranking
        ranked_developments, cluster_info = stage_cluster_and_rank(
            annotated_articles,
            domain_cfg,
            n_clusters=min(6, max(2, len(annotated_articles) // 3)),
        )
        logger.info(f"Identified {len(cluster_info)} clusters, selected top {len(ranked_developments)} developments.")

        # Stage 5: Report Generation
        state.transition_to(PipelineStatus.GENERATING)
        report_payload, html_report, email_html, email_text = stage_render(
            domain_cfg=domain_cfg,
            ranked_developments=ranked_developments,
            total_articles=len(clean_articles),
            report_date=target_date,
            templates_dir=TEMPLATES_DIR,
        )

        # Validation Check
        is_valid, issues = validate_report(report_payload)
        if not is_valid:
            logger.warning(f"Report validation warnings: {issues}")

        # Save Artifacts
        report_file = out_dir / f"daily_brief_{domain_id}_{target_date}.html"
        email_html_file = prev_dir / f"daily_email_{domain_id}_{target_date}.html"
        email_txt_file = prev_dir / f"daily_email_{domain_id}_{target_date}.txt"
        json_meta_file = out_dir / f"daily_brief_{domain_id}_{target_date}.json"

        report_file.write_text(html_report, encoding="utf-8")
        email_html_file.write_text(email_html, encoding="utf-8")
        email_txt_file.write_text(email_text, encoding="utf-8")
        json_meta_file.write_text(
            json.dumps(report_payload.model_dump(), default=str, indent=2),
            encoding="utf-8",
        )

        state.reports_generated = 1
        state.transition_to(PipelineStatus.ARCHIVED)
        logger.info(f"Report artifacts successfully written to '{out_dir}' and '{prev_dir}'.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        state.transition_to(PipelineStatus.FAILED, error=str(e))

    return state


def main():
    """CLI Entry Point."""
    parser = argparse.ArgumentParser(
        prog="signalbrief",
        description="SignalBrief — AI-Powered Daily Intelligence Briefing Engine",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute the daily intelligence pipeline")
    run_parser.add_argument("--domain", default="manufacturing", help="Domain ID (default: manufacturing)")
    run_parser.add_argument("--date", default=None, help="Run date YYYY-MM-DD (default: today)")
    run_parser.add_argument("--output-dir", default=None, help="Output directory for generated HTML reports")
    run_parser.add_argument("--preview-dir", default=None, help="Output directory for email previews")

    # Command: sources
    src_parser = subparsers.add_parser("sources", help="List configured sources for a domain")
    src_parser.add_argument("--domain", default="manufacturing", help="Domain ID")

    # Command: validate
    val_parser = subparsers.add_parser("validate", help="Validate configurations and pipeline schemas")
    val_parser.add_argument("--domain", default="manufacturing", help="Domain ID")

    args = parser.parse_args()

    # Default to 'run' if no command specified but arguments passed
    if args.command is None:
        args.command = "run"
        args.domain = "manufacturing"
        args.date = None
        args.output_dir = None
        args.preview_dir = None

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.command == "run":
        out_dir = Path(args.output_dir) if args.output_dir else None
        prev_dir = Path(args.preview_dir) if args.preview_dir else None
        state = run_daily_pipeline(
            domain_id=args.domain,
            run_date=args.date,
            output_dir=out_dir,
            preview_dir=prev_dir,
        )
        print("\n==========================================")
        print(f" SignalBrief Pipeline: {state.status.value.upper()}")
        print(f" Run ID:             {state.run_id}")
        print(f" Articles Ingested:  {state.articles_collected}")
        print(f" Articles Analyzed:  {state.articles_processed}")
        print(f" Reports Generated:  {state.reports_generated}")
        if state.error_message:
            print(f" Error:              {state.error_message}")
            sys.exit(1)
        print("==========================================\n")

    elif args.command == "sources":
        sources = load_sources_for_domain(args.domain)
        print(f"\nConfigured sources for '{args.domain}':")
        for s in sources:
            status = "ACTIVE" if s.active else "INACTIVE"
            print(f" - [{status:8}] {s.id:<25} ({s.source_type}) -> {s.endpoint}")

    elif args.command == "validate":
        pipe_cfg = load_pipeline_config()
        dom_cfg = load_domain_config(args.domain)
        srcs = load_sources_for_domain(args.domain)
        print(f"\n[OK] Pipeline config '{pipe_cfg.name}' loaded.")
        print(f"[OK] Domain config '{dom_cfg.name}' ({dom_cfg.id}) loaded.")
        print(f"[OK] {len(srcs)} sources loaded ({sum(1 for s in srcs if s.active)} active).")


if __name__ == "__main__":
    main()
