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


def test_triadic_synthesis_centroid_url_fallback():
    """Verify centroid URL fallback when member articles have no valid URLs."""
    cluster = {
        "cluster_id": 2,
        "theme_label": "Supply Chain Logistics",
        "centroid_title": "Port congestion eases across West Coast terminals",
        "centroid_article_id": "art_centroid_1",
        "centroid_url": "https://www.transportation.gov/news/ports-update",
        "sources": ["dot_feed"],
        "composite_score": 0.91,
        "member_articles": [
            {"id": "a1", "source_id": "dot_feed", "title": "Update", "url": ""},
            {"id": "a2", "source_id": "dot_feed", "title": "Notice", "url": None},
        ],
    }
    dev = synthesize_triad_from_cluster(cluster)
    assert len(dev.sources) == 1
    assert dev.sources[0].url == "https://www.transportation.gov/news/ports-update"
    assert dev.sources[0].source_name == "Dot Feed"


def test_triadic_synthesis_canonical_url_and_iteration():
    """Verify canonical URL fallback and scanning member articles beyond the first 4."""
    cluster = {
        "cluster_id": 3,
        "theme_label": "Advanced Materials",
        "centroid_title": "Ceramic composite breakthroughs in aerospace manufacturing",
        "sources": ["feed_a", "feed_b"],
        "composite_score": 0.85,
        "member_articles": [
            {"id": "a1", "source_id": "feed_a", "title": "Dup 1", "url": "https://example.com/item1"},
            {"id": "a2", "source_id": "feed_a", "title": "Dup 2", "url": "https://example.com/item1"},  # duplicate
            {"id": "a3", "source_id": "feed_a", "title": "No URL", "url": ""},
            {"id": "a4", "source_id": "feed_a", "title": "No URL", "url": None},
            {"id": "a5", "source_id": "feed_b", "title": "Canonical Only", "url": "", "url_canonical": "https://example.com/canonical-item"},
            {"id": "a6", "source_id": "feed_b", "title": "Valid Item", "url": "https://example.com/item2"},
        ],
    }
    dev = synthesize_triad_from_cluster(cluster)
    assert len(dev.sources) == 3
    urls = [s.url for s in dev.sources]
    assert "https://example.com/item1" in urls
    assert "https://example.com/canonical-item" in urls
    assert "https://example.com/item2" in urls


def test_build_daily_report_payload_filters_uncited_developments():
    """Verify build_daily_report_payload retains only cited developments if uncited exist."""
    cited_cluster = {
        "cluster_id": 1,
        "theme_label": "Robotics",
        "centroid_title": "Robotics deployment",
        "sources": ["src1"],
        "composite_score": 0.8,
        "member_articles": [{"id": "a1", "source_id": "src1", "title": "Title 1", "url": "https://example.com/1"}],
    }
    uncited_cluster = {
        "cluster_id": 2,
        "theme_label": "Rumor",
        "centroid_title": "Unsubstantiated rumor",
        "sources": [],
        "composite_score": 0.5,
        "member_articles": [{"id": "a2", "source_id": "src2", "title": "No link", "url": ""}],
    }
    report = build_daily_report_payload(
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        ranked_developments=[cited_cluster, uncited_cluster],
        total_articles_monitored=30,
    )
    assert len(report.developments) == 1
    assert report.developments[0].headline.startswith("Robotics")
    assert all(len(d.sources) > 0 for d in report.developments)


