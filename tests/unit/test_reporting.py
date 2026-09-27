"""Unit tests for report synthesis, Jinja2 rendering, and editorial validation."""

from signalbrief.config.defaults import TEMPLATES_DIR
from signalbrief.reporting.renderer import render_email_html, render_email_text, render_html_report
from signalbrief.reporting.report_schema import Citation, DailyReport, ReportDevelopment
from signalbrief.reporting.summarization import (
    build_daily_report_payload,
    synthesize_triad_from_cluster,
)
from signalbrief.reporting.validation import validate_report


def test_triadic_synthesis():
    """Verify cluster converts into structured triadic development."""
    cluster = {
        "cluster_id": 1,
        "theme_label": "Industrial Robotics",
        "centroid_title": "Automated mobile robots deployed across assembly plant",
        "sources": ["nist", "robot_report"],
        "composite_score": 0.88,
        "member_articles": [
            {
                "id": "a1",
                "source_id": "nist",
                "title": "NIST awards smart factory grant",
                "url": "https://www.nist.gov/news/grant-01",
                "subtopic": "industrial_ai",
            }
        ],
    }
    dev = synthesize_triad_from_cluster(cluster)
    assert isinstance(dev, ReportDevelopment)
    assert dev.topic_label == "Industrial Robotics"
    assert len(dev.what_changed) > 10
    assert len(dev.why_it_matters) > 20
    assert len(dev.what_to_watch) > 20
    assert len(dev.sources) == 1
    assert dev.sources[0].url == "https://www.nist.gov/news/grant-01"


def test_build_daily_report_payload():
    """Verify building complete daily report payload."""
    cluster = {
        "cluster_id": 1,
        "theme_label": "Automation",
        "centroid_title": "Factory floor upgrades",
        "sources": ["src1"],
        "composite_score": 0.75,
        "member_articles": [
            {"id": "a1", "source_id": "src1", "title": "Upgrade", "url": "https://example.com/1"}
        ],
    }
    report = build_daily_report_payload(
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        ranked_developments=[cluster],
        total_articles_monitored=25,
    )
    assert isinstance(report, DailyReport)
    assert report.domain_id == "manufacturing"
    assert len(report.developments) == 1
    assert report.article_count == 25


def test_report_validation_pass():
    """Verify validation passes on a conforming report."""
    dev = ReportDevelopment(
        id="dev_1",
        headline="Major industrial automation initiative announced",
        what_changed="Federal grant program funds 10 smart factory automation hubs.",
        why_it_matters="Accelerates technology adoption and domestic supply chain resilience.",
        what_to_watch="Grant application deadlines and partner university announcements.",
        topic_label="Industrial AI",
        sources=[
            Citation(
                article_id="art_1",
                source_name="NIST",
                title="Grant announcement",
                url="https://www.nist.gov/article-1",
            )
        ],
    )
    report = DailyReport(
        id="rep_1",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Comprehensive overview of today's key manufacturing advances and supply chain shifts.",
        developments=[dev],
        article_count=10,
    )
    is_valid, issues = validate_report(report)
    assert is_valid is True
    assert len(issues) == 0


def test_report_validation_fail_missing_citation():
    """Verify validation catches developments with missing citations."""
    dev = ReportDevelopment(
        id="dev_2",
        headline="Unsubstantiated factory rumor",
        what_changed="Some rumor changed the status of factories today.",
        why_it_matters="It matters because of potential operational disruptions.",
        what_to_watch="Watch for future announcements in the industry.",
        sources=[],  # Violates 100% citation coverage
    )
    report = DailyReport(
        id="rep_2",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Summary of rumors and developments across the manufacturing sector.",
        developments=[dev],
    )
    is_valid, issues = validate_report(report)
    assert is_valid is False
    assert any("0 sources" in issue for issue in issues)


def test_render_templates():
    """Verify Jinja2 rendering of HTML report and emails."""
    dev = ReportDevelopment(
        id="dev_1",
        headline="NIST announces new grant",
        what_changed="Grant allocated for automation.",
        why_it_matters="Improves factory competitiveness.",
        what_to_watch="Application deadlines.",
        topic_label="Automation",
        sources=[Citation(article_id="a1", source_name="NIST", title="Grant", url="https://example.com/grant")],
    )
    report = DailyReport(
        id="rep_test",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Today's briefing on manufacturing.",
        developments=[dev],
        what_to_watch_next=["Quarterly shipments report."],
        article_count=10,
    )
    html_out = render_html_report(report, TEMPLATES_DIR)
    assert "<!DOCTYPE html>" in html_out
    assert "Manufacturing" in html_out
    assert "NIST announces new grant" in html_out

    email_html = render_email_html(report, "https://signalbrief.local/rep", TEMPLATES_DIR)
    assert "<!DOCTYPE html>" in email_html
    assert "Know what changed" in email_html

    email_txt = render_email_text(report, "https://signalbrief.local/rep", TEMPLATES_DIR)
    assert "MANUFACTURING INTELLIGENCE" in email_txt
    assert "SIGNALBRIEF" in email_txt

