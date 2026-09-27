"""Reporting module for schemas, template rendering, and brief synthesis."""

from signalbrief.reporting.renderer import (
    render_email_html,
    render_email_text,
    render_html_report,
)
from signalbrief.reporting.report_schema import (
    Citation,
    DailyReport,
    ReportDevelopment,
)
from signalbrief.reporting.summarization import (
    build_daily_report_payload,
    synthesize_triad_from_cluster,
)

__all__ = [
    "Citation",
    "DailyReport",
    "ReportDevelopment",
    "render_email_html",
    "render_email_text",
    "render_html_report",
    "build_daily_report_payload",
    "synthesize_triad_from_cluster",
]
