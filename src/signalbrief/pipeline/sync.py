"""Cloudflare edge synchronization client for SignalBrief daily reports."""

import logging
import time
from typing import Any, Dict, Optional
import requests

from signalbrief.reporting.report_schema import DailyReport
from signalbrief.reporting.validation import validate_report

logger = logging.getLogger("signalbrief.sync")


class ReportSyncError(Exception):
    """Raised when synchronization with Cloudflare edge fails."""
    pass


def sync_report_to_cloudflare(
    report_payload: DailyReport,
    html_content: str,
    api_url: str,
    internal_key: str,
    email_html: Optional[str] = None,
    email_text: Optional[str] = None,
    dispatch_email: bool = False,
    articles_collected: int = 0,
    articles_processed: int = 0,
    duration_seconds: float = 0.0,
    job_id: Optional[str] = None,
    relevant_articles: int = 0,
    clusters_formed: int = 0,
    max_retries: int = 3,
    timeout_sec: int = 30,
) -> Dict[str, Any]:
    """Synchronize a validated daily report with Cloudflare Worker D1 and R2.

    Args:
        report_payload: The validated DailyReport pydantic object.
        html_content: The rendered standalone HTML5 report string.
        api_url: Base URL of the Cloudflare Worker API (e.g. https://api.signalbrief.local).
        internal_key: Bearer token matching SIGNALBRIEF_INTERNAL_KEY.
        email_html: Optional HTML email body.
        email_text: Optional plain-text email body.
        dispatch_email: Whether to trigger subscriber email dispatch upon ingestion.
        articles_collected: Total raw articles collected.
        articles_processed: Total cleaned articles processed.
        duration_seconds: Total pipeline runtime.
        max_retries: Maximum HTTP retry attempts for transient network issues.
        timeout_sec: HTTP request timeout in seconds.

    Returns:
        Dict containing Cloudflare response metadata (report_id, r2_key, etc.).
    """
    # 1. Pre-flight local validation
    is_valid, issues = validate_report(report_payload)
    if not is_valid:
        raise ReportSyncError(f"Cannot sync invalid report: {'; '.join(issues)}")

    endpoint = f"{api_url.rstrip('/')}/api/internal/report"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {internal_key.strip()}",
        "User-Agent": "SignalBrief-Python-Runner/1.0",
    }

    payload = {
        "report": report_payload.model_dump(),
        "html": html_content,
        "email_html": email_html,
        "email_text": email_text,
        "dispatch_email": dispatch_email,
        "articles_collected": articles_collected,
        "articles_processed": articles_processed,
        "relevant_articles": relevant_articles,
        "clusters_formed": clusters_formed,
        "duration_seconds": duration_seconds,
        "job_id": job_id,
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Syncing report '{report_payload.id}' to Cloudflare edge (attempt {attempt}/{max_retries})..."
            )
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=timeout_sec,
            )

            if response.status_code in (200, 201):
                data = response.json()
                logger.info(
                    f"Successfully synchronized report '{report_payload.id}' (R2 Key: {data.get('r2_key')})."
                )
                return data

            if response.status_code == 401:
                raise ReportSyncError("Authentication failed: invalid SIGNALBRIEF_INTERNAL_KEY.")

            if 400 <= response.status_code < 500:
                raise ReportSyncError(f"Client error from Worker API ({response.status_code}): {response.text}")

            # 5xx server errors can be retried
            last_error = f"Worker API error ({response.status_code}): {response.text}"
            logger.warning(f"Transient error on attempt {attempt}: {last_error}")

        except (requests.ConnectionError, requests.Timeout) as net_err:
            last_error = f"Network error connecting to {endpoint}: {net_err}"
            logger.warning(f"Connection issue on attempt {attempt}: {last_error}")

        if attempt < max_retries:
            backoff = 2 ** attempt
            time.sleep(backoff)

    raise ReportSyncError(f"Failed to sync report to Cloudflare after {max_retries} attempts. Last error: {last_error}")
