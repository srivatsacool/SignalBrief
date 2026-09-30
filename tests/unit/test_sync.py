"""Unit tests for Cloudflare edge synchronization client."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from signalbrief.pipeline.sync import ReportSyncError, sync_report_to_cloudflare
from signalbrief.reporting.report_schema import Citation, DailyReport, ReportDevelopment


@pytest.fixture
def sample_report():
    return DailyReport(
        id="rep_sync_test",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-29",
        executive_summary="Summary of manufacturing advances.",
        developments=[
            ReportDevelopment(
                id="dev_01",
                headline="Robotics in Automotive",
                what_changed="Automation upgraded.",
                why_it_matters="Efficiency improved.",
                what_to_watch="Shipments next month.",
                topic_label="Robotics",
                sources=[
                    Citation(
                        article_id="art_01",
                        source_name="NIST",
                        title="Robotics Study",
                        url="https://example.com/robotics",
                    )
                ],
            )
        ],
    )


def test_sync_preflight_validation_failure():
    """Verify sync rejects invalid reports before sending network requests."""
    invalid_report = DailyReport(
        id="rep_invalid",
        domain_id="manufacturing",
        domain_name="Manufacturing",
        report_date="2026-09-29",
        executive_summary="Summary",
        developments=[
            ReportDevelopment(
                id="dev_uncited",
                headline="Uncited development",
                what_changed="Something changed",
                why_it_matters="It matters",
                what_to_watch="Watch this",
                sources=[],  # 0 citations violates validation
            )
        ],
    )
    with pytest.raises(ReportSyncError, match="Cannot sync invalid report"):
        sync_report_to_cloudflare(
            report_payload=invalid_report,
            html_content="<html></html>",
            api_url="https://api.test",
            internal_key="secret",
        )


def test_sync_success(sample_report):
    """Verify successful report synchronization with Cloudflare edge."""
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "success": True,
        "report_id": "rep_sync_test",
        "r2_key": "reports/2026/09/29/rep_sync_test.html",
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        res = sync_report_to_cloudflare(
            report_payload=sample_report,
            html_content="<html><body>Report</body></html>",
            api_url="https://api.signalbrief.test",
            internal_key="my-secret-key",
            dispatch_email=True,
        )

        assert res["success"] is True
        assert res["r2_key"] == "reports/2026/09/29/rep_sync_test.html"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.signalbrief.test/api/internal/report"
        assert kwargs["headers"]["Authorization"] == "Bearer my-secret-key"
        assert kwargs["json"]["dispatch_email"] is True


def test_sync_auth_failure(sample_report):
    """Verify 401 raises ReportSyncError immediately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"

    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(ReportSyncError, match="Authentication failed"):
            sync_report_to_cloudflare(
                report_payload=sample_report,
                html_content="<html></html>",
                api_url="https://api.test",
                internal_key="bad-key",
            )


def test_sync_retry_on_network_error(sample_report):
    """Verify sync retries on network connection errors."""
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"success": True, "report_id": "rep_sync_test"}

    # Fail once with connection error, then succeed
    side_effects = [
        requests.ConnectionError("Connection refused"),
        mock_resp,
    ]

    with patch("requests.post", side_effect=side_effects):
        with patch("time.sleep", return_value=None):
            res = sync_report_to_cloudflare(
                report_payload=sample_report,
                html_content="<html></html>",
                api_url="https://api.test",
                internal_key="secret",
                max_retries=2,
            )
            assert res["success"] is True
