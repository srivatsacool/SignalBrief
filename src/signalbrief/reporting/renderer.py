"""Jinja2 template renderer for HTML reports and email briefs."""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from signalbrief.config.defaults import TEMPLATES_DIR
from signalbrief.reporting.report_schema import DailyReport


def get_jinja_env(templates_dir: Optional[Path] = None) -> Environment:
    """Initialize Jinja2 Environment with autoescape and safe loader."""
    root = templates_dir or TEMPLATES_DIR
    return Environment(
        loader=FileSystemLoader(str(root)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_html_report(report: DailyReport, templates_dir: Optional[Path] = None) -> str:
    """Render a responsive HTML daily intelligence brief."""
    env = get_jinja_env(templates_dir)
    template = env.get_template("reports/daily_report.html.jinja2")
    return template.render(**report.model_dump())


def render_email_html(report: DailyReport, report_url: str, templates_dir: Optional[Path] = None) -> str:
    """Render responsive HTML email body."""
    env = get_jinja_env(templates_dir)
    template = env.get_template("emails/daily_email.html.jinja2")
    context = report.model_dump()
    context["report_url"] = report_url
    return template.render(**context)


def render_email_text(report: DailyReport, report_url: str, templates_dir: Optional[Path] = None) -> str:
    """Render plain text email body."""
    env = get_jinja_env(templates_dir)
    template = env.get_template("emails/daily_email.txt.jinja2")
    context = report.model_dump()
    context["report_url"] = report_url
    return template.render(**context)
