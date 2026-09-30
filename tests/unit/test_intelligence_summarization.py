"""Unit tests for the 5-part intelligence summarization framework, zero-boilerplate policy, and benchmark evaluation."""

import json
from pathlib import Path

import pytest
from signalbrief.reporting.report_schema import ReportDevelopment
from signalbrief.reporting.summarization import (
    clean_headline,
    detect_event_type,
    synthesize_triad_from_cluster,
)

BENCHMARK_PATH = Path(__file__).parents[2] / "data" / "evaluation" / "summarization_benchmark.json"

BANNED_BOILERPLATE_SUBSTRINGS = [
    "signals accelerating momentum",
    "impacting strategic capital allocation",
    "implementation timelines, vendor integration benchmarks",
    "tracked initiatives",
    "monitored across reporting channels",
]


@pytest.fixture
def benchmark_cases():
    assert BENCHMARK_PATH.exists(), f"Benchmark file missing at {BENCHMARK_PATH}"
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_five_part_structure_and_completeness(benchmark_cases):
    """Verify that all benchmark clusters produce complete 5-part intelligence developments."""
    for case in benchmark_cases:
        dev = synthesize_triad_from_cluster(case, domain_name="Manufacturing")
        assert isinstance(dev, ReportDevelopment)

        # 1. Headline
        assert dev.headline, f"Headline missing in {case['id']}"
        assert not dev.headline.endswith("..."), f"Headline has trailing ellipsis: {dev.headline}"
        assert not dev.headline.endswith("…"), f"Headline has trailing ellipsis: {dev.headline}"

        # 2. What Happened (what_changed)
        assert dev.what_changed, f"What happened missing in {case['id']}"
        assert len(dev.what_changed) > 20, f"What happened too short in {case['id']}"

        # 3. Why It Matters
        assert dev.why_it_matters, f"Why it matters missing in {case['id']}"
        assert len(dev.why_it_matters) > 30, f"Why it matters too short in {case['id']}"

        # 4. Business Implications
        assert dev.business_implications, f"Business implications missing in {case['id']}"
        assert len(dev.business_implications) > 30, f"Business implications too short in {case['id']}"

        # 5. What To Watch
        assert dev.what_to_watch, f"What to watch missing in {case['id']}"
        assert len(dev.what_to_watch) > 30, f"What to watch too short in {case['id']}"

        # 6. Source Attribution
        assert len(dev.sources) > 0, f"Zero sources in {case['id']}"
        assert dev.sources[0].url.startswith("http"), f"Invalid source URL in {case['id']}"


def test_zero_banned_boilerplate_phrases(benchmark_cases):
    """Verify strictly zero occurrences of banned mad-libs boilerplate phrases."""
    for case in benchmark_cases:
        dev = synthesize_triad_from_cluster(case, domain_name="Manufacturing")
        composite_text = " ".join([
            dev.headline,
            dev.what_changed,
            dev.why_it_matters,
            dev.business_implications or "",
            dev.what_to_watch,
        ]).lower()

        for banned in BANNED_BOILERPLATE_SUBSTRINGS:
            assert banned not in composite_text, (
                f"Found banned boilerplate phrase '{banned}' in {case['id']}:\n{composite_text}"
            )


def test_clean_headline_sanitization():
    """Verify headlines are stripped of source attribution trailers and trailing punctuation."""
    raw_1 = "Lego breaks ground on $400M plant in Virginia - Manufacturing Dive"
    clean_1 = clean_headline("Capital Expansion", raw_1)
    assert "- Manufacturing Dive" not in clean_1
    assert clean_1.startswith("Capital Expansion: ")
    assert not clean_1.endswith(".")

    raw_2 = "USPS warns of processing delays due to upgrades | Reuters..."
    clean_2 = clean_headline("Logistics", raw_2)
    assert "| Reuters" not in clean_2
    assert not clean_2.endswith("...")
    assert not clean_2.endswith("…")


def test_event_type_classification(benchmark_cases):
    """Verify event types are accurately determined for each benchmark category."""
    for case in benchmark_cases:
        text = f"{case['centroid_title']} {case['theme_label']}"
        subtopic = case["member_articles"][0].get("subtopic", "")
        detected = detect_event_type(text, subtopic)
        assert detected == case["expected_event_type"], (
            f"Event type mismatch for {case['id']}: expected {case['expected_event_type']}, got {detected}"
        )


def test_metrics_and_entities_preserved(benchmark_cases):
    """Verify that concrete metrics ($M, $B, %) in articles are carried into factual leads or significance."""
    for case in benchmark_cases:
        expected_metrics = case.get("expected_metrics", [])
        if not expected_metrics:
            continue

        dev = synthesize_triad_from_cluster(case, domain_name="Manufacturing")
        all_text = f"{dev.headline} {dev.what_changed} {dev.why_it_matters}"

        # At least one metric variation should appear
        matched = any(m.lower() in all_text.lower() for m in expected_metrics)
        assert matched, (
            f"None of expected metrics {expected_metrics} found in {case['id']} output:\n{all_text}"
        )
