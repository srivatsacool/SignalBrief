"""Analytical quality and evaluation benchmark tests."""

import hashlib
import json
from pathlib import Path

from signalbrief.analytics.classification import classify_subtopic
from signalbrief.analytics.sentiment import analyze_sentiment
from signalbrief.config.defaults import DATA_DIR
from signalbrief.reporting.report_schema import Citation, DailyReport, ReportDevelopment
from signalbrief.reporting.validation import validate_report


def test_gold_standard_benchmark_accuracy():
    """Verify subtopic classification and sentiment accuracy on gold standard benchmark."""
    benchmark_path = DATA_DIR / "evaluation" / "gold_standard_benchmark.json"
    if not benchmark_path.exists():
        # Fallback if running outside root
        benchmark_path = Path("data/evaluation/gold_standard_benchmark.json")

    assert benchmark_path.exists(), f"Benchmark file missing: {benchmark_path}"

    with open(benchmark_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    subtopic_matches = 0
    sentiment_matches = 0

    for c in cases:
        text = c["text"]
        pred_subtopic, _ = classify_subtopic(text)
        pred_sentiment, _ = analyze_sentiment(text)

        # Normalize strings for comparison
        clean_pred_sub = pred_subtopic.replace("_", " ").lower()
        clean_exp_sub = c["expected_subtopic"].lower()
        if clean_pred_sub == clean_exp_sub:
            subtopic_matches += 1

        if pred_sentiment == c["expected_sentiment"]:
            sentiment_matches += 1

    subtopic_acc = subtopic_matches / len(cases)
    sentiment_acc = sentiment_matches / len(cases)

    # Acceptance criterion: Accuracy >= 80%
    assert subtopic_acc >= 0.80, f"Subtopic accuracy below 80%: {subtopic_acc:.2%}"
    assert sentiment_acc >= 0.80, f"Sentiment accuracy below 80%: {sentiment_acc:.2%}"


def test_strict_citation_coverage():
    """Verify that any report development without a citation is rejected."""
    unverified_dev = ReportDevelopment(
        id="dev_nocite",
        headline="Major robotic takeover of all manufacturing facilities",
        what_changed="Automation replaces 100% of factory workers.",
        why_it_matters="Massive operational shift with unverified claims.",
        what_to_watch="Regulatory response and workforce strikes.",
        sources=[],  # Violates 100% citation coverage rule
    )

    report = DailyReport(
        id="rep_unverified",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Summary of unverified assertions across the industrial sector.",
        developments=[unverified_dev],
    )

    is_valid, issues = validate_report(report)
    assert is_valid is False
    assert any("0 sources" in err for err in issues)


def test_idempotent_report_generation():
    """Verify that identical inputs produce identical deterministic payloads."""
    dev = ReportDevelopment(
        id="dev_deterministic",
        headline="NIST funds manufacturing extension partnership centers",
        what_changed="NIST awards $30M to MEP centers across the nation.",
        why_it_matters="Accelerates technology adoption among small and medium manufacturers.",
        what_to_watch="Application deadlines and initial center grant rollouts.",
        sources=[
            Citation(
                article_id="nist_01",
                source_name="NIST",
                title="MEP Award",
                url="https://www.nist.gov/mep-award",
            )
        ],
    )

    from datetime import datetime, timezone
    fixed_time = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    r1 = DailyReport(
        id="rep_fixed",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Deterministic test briefing for manufacturing domain.",
        developments=[dev],
        created_at=fixed_time,
    )
    r2 = DailyReport(
        id="rep_fixed",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Deterministic test briefing for manufacturing domain.",
        developments=[dev],
        created_at=fixed_time,
    )

    # Hashes of JSON representations must be identical
    h1 = hashlib.sha256(json.dumps(r1.model_dump(), default=str, sort_keys=True).encode()).hexdigest()
    h2 = hashlib.sha256(json.dumps(r2.model_dump(), default=str, sort_keys=True).encode()).hexdigest()
    assert h1 == h2

