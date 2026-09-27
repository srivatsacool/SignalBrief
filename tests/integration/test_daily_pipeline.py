"""Integration tests for the end-to-end SignalBrief daily pipeline."""

import json
from pathlib import Path

from signalbrief.pipeline.daily import run_daily_pipeline
from signalbrief.pipeline.run_state import PipelineStatus
from signalbrief.preprocessing.validation import CleanArticle


def test_full_pipeline_with_sample_articles(tmp_path: Path):
    """Execute stages 3 through 5 using simulated clean articles and verify artifacts."""
    sample_articles = [
        CleanArticle(
            id=f"art_mfg_{i}",
            source_id="nist" if i % 2 == 0 else "manufacturing_dive",
            domain_id="manufacturing",
            title=f"Advanced Robotics Automation Update #{i} in Assembly Plants",
            url=f"https://example.com/articles/mfg-{i}",
            url_canonical=f"https://example.com/articles/mfg-{i}",
            content_hash=f"hash_{i}_abcdef123456",
            clean_text=(
                f"Industrial automation and robotics systems accelerate factory floor throughput. "
                f"Equipment manufacturers deploy AI sensors and computer vision across production lines {i}."
            ),
            word_count=24,
            language="en",
        )
        for i in range(12)
    ]

    out_dir = tmp_path / "generated"
    prev_dir = tmp_path / "previews"

    state = run_daily_pipeline(
        domain_id="manufacturing",
        run_date="2026-09-28",
        output_dir=out_dir,
        preview_dir=prev_dir,
        cached_clean_articles=sample_articles,
    )

    # Verify pipeline completed successfully
    assert state.status == PipelineStatus.ARCHIVED
    assert state.articles_collected == 12
    assert state.articles_processed == 12
    assert state.reports_generated == 1
    assert state.error_message is None

    # Verify generated artifacts
    html_file = out_dir / "daily_brief_manufacturing_2026-09-28.html"
    json_file = out_dir / "daily_brief_manufacturing_2026-09-28.json"
    email_html = prev_dir / "daily_email_manufacturing_2026-09-28.html"
    email_txt = prev_dir / "daily_email_manufacturing_2026-09-28.txt"

    assert html_file.exists()
    assert json_file.exists()
    assert email_html.exists()
    assert email_txt.exists()

    # Verify HTML contents
    html_content = html_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_content
    assert "Manufacturing" in html_content
    assert "what changed" in html_content.lower()
    assert "why it matters" in html_content.lower()
    assert "what to watch" in html_content.lower()


    # Verify JSON structure
    report_dict = json.loads(json_file.read_text(encoding="utf-8"))
    assert report_dict["domain_id"] == "manufacturing"
    assert len(report_dict["developments"]) >= 1
    for dev in report_dict["developments"]:
        assert len(dev["sources"]) >= 1
        assert dev["what_changed"]
        assert dev["why_it_matters"]
        assert dev["what_to_watch"]
