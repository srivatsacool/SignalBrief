"""Unit tests for configuration loaders and template rendering."""

from signalbrief.config.loader import (
    list_available_domains,
    load_domain_config,
    load_pipeline_config,
    load_sources_for_domain,
)
from signalbrief.preprocessing.cleaning import clean_article_text, count_words
from signalbrief.reporting.renderer import render_email_html, render_email_text, render_html_report
from signalbrief.reporting.report_schema import Citation, DailyReport, ReportDevelopment


def test_load_pipeline_config():
    cfg = load_pipeline_config()
    assert cfg.name == "SignalBrief Daily Intelligence Pipeline"
    assert cfg.collection.lookback_hours == 48
    assert cfg.analytics.max_developments_per_report == 5


def test_load_manufacturing_domain():
    cfg = load_domain_config("manufacturing")
    assert cfg.id == "manufacturing"
    assert "industrial automation" in cfg.keywords
    assert len(cfg.subtopics) > 0


def test_list_domains():
    domains = list_available_domains()
    assert "manufacturing" in domains
    assert "supply_chain" in domains


def test_load_sources():
    sources = load_sources_for_domain("manufacturing")
    assert len(sources) >= 3
    for s in sources:
        assert s.feed_url.startswith("http")


def test_clean_article_text():
    html = "<p>Factory digitization is <b>accelerating</b> in 2026.<script>alert('spam');</script></p>"
    cleaned = clean_article_text(html)
    assert "alert" not in cleaned
    assert "Factory digitization is accelerating in 2026." == cleaned
    assert count_words(cleaned) == 6


def test_render_report():
    report = DailyReport(
        id="test_report_001",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Manufacturing technology is experiencing unprecedented automation.",
        developments=[
            ReportDevelopment(
                id="dev_01",
                headline="Breakthrough in Autonomous Robotics on Assembly Lines",
                what_changed="New vision models deployed across assembly plants.",
                why_it_matters="Reduces defect rates by 40% and speeds up cycle time.",
                what_to_watch="Regulatory standards updates next month.",
                topic_label="Industrial Robotics",
                sources=[
                    Citation(
                        article_id="art_01",
                        source_name="NIST",
                        title="Standards for Autonomous Robotics",
                        url="https://www.nist.gov/sample-article",
                    )
                ],
            )
        ],
        what_to_watch_next=["Quarterly industrial output index report"],
        article_count=15,
    )
    html = render_html_report(report)
    assert "Breakthrough in Autonomous Robotics" in html
    assert "NIST" in html
    assert "Know what changed. Understand why it matters. See what to watch next." in html

    email_html = render_email_html(report, report_url="https://signalbrief.local/reports/test_report_001")
    assert "Breakthrough in Autonomous Robotics" in email_html

    email_txt = render_email_text(report, report_url="https://signalbrief.local/reports/test_report_001")
    assert "EXECUTIVE SUMMARY" in email_txt
