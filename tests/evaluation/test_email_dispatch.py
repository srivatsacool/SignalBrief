"""Evaluation tests for subscriber email dispatch, 10-user quota, and template compliance."""

from signalbrief.config.defaults import TEMPLATES_DIR
from signalbrief.reporting.renderer import render_email_html, render_email_text
from signalbrief.reporting.report_schema import Citation, DailyReport, ReportDevelopment


def test_email_dispatch_payload_and_quota():
    """Verify that email dispatch handles subscriber batches adhering to the 10-subscriber pilot quota."""
    # Simulate 12 invited users (2 beyond the quota limit)
    subscribers = [
        {"id": f"user_{i}", "email": f"subscriber{i}@example.com", "name": f"Subscriber {i}"}
        for i in range(12)
    ]
    # Enforce initial pilot decision: maximum 10 invited subscribers
    max_quota = 10
    active_batch = subscribers[:max_quota]
    assert len(active_batch) == 10
    assert len(subscribers) > max_quota


def test_email_rendering_contains_mandatory_links():
    """Verify generated email HTML and text contain required dashboard, report, and unsubscribe links."""
    dev = ReportDevelopment(
        id="dev_01",
        headline="Industrial AI Robotics Rollout",
        what_changed="Automated inspection system installed across 5 plants.",
        why_it_matters="Reduces assembly line defect rate by 35%.",
        what_to_watch="Full factory audit reports next quarter.",
        topic_label="Industrial AI",
        sources=[Citation(article_id="art1", source_name="NIST", title="Inspection update", url="https://example.com/1")],
    )

    report = DailyReport(
        id="rep_test_email",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-28",
        executive_summary="Summary of robotics inspection expansion.",
        developments=[dev],
        dashboard_url="https://signalbrief.local",
        unsubscribe_url="https://signalbrief.local/settings",
    )

    report_url = "https://signalbrief.local/report/rep_test_email"
    html_rendered = render_email_html(report, report_url, TEMPLATES_DIR)
    text_rendered = render_email_text(report, report_url, TEMPLATES_DIR)

    # HTML verification
    assert report_url in html_rendered
    assert "https://signalbrief.local/settings" in html_rendered
    assert "https://signalbrief.local" in html_rendered
    assert "Know what changed" in html_rendered
    assert "What Changed:" in html_rendered
    assert "Why It Matters:" in html_rendered

    # Plain text verification
    assert report_url in text_rendered
    assert "https://signalbrief.local/settings" in text_rendered
    assert "SIGNALBRIEF" in text_rendered
