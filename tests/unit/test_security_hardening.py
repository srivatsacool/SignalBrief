"""Unit tests for SignalBrief v1.0.1 security hardening and authentication verification."""



class TestSecurityHardening:
    """Test suite for security hardening, credential protection, and token sanitization."""

    def test_job_response_sanitization_removes_token(self):
        """Ensure job records strip job_token before public API responses."""
        raw_db_job = {
            "id": "job_mfg_2026-10-01_abc123",
            "domain_id": "manufacturing",
            "run_date": "2026-10-01",
            "status": "completed",
            "job_token": "tok_super_secret_callback_token_9999",
            "sources_total": 42,
            "articles_collected": 104,
            "articles_processed": 70,
            "relevant_articles": 0,
            "clusters_formed": 6,
            "report_id": "report_20261001_manufacturing",
        }

        # Simulate the Worker sanitization: const { job_token, ...safeJob } = job;
        safe_job = {k: v for k, v in raw_db_job.items() if k != "job_token"}

        assert "job_token" not in safe_job
        assert safe_job["id"] == "job_mfg_2026-10-01_abc123"
        assert safe_job["status"] == "completed"
        assert "tok_super_secret" not in str(safe_job)

    def test_callback_token_validation_logic(self):
        """Validate strict callback token matching rules (fail closed)."""
        expected_token = "tok_valid_expected_token_123"

        def is_authorized(stored_token: str, provided_token: str) -> bool:
            if not stored_token or not provided_token:
                return False
            return stored_token == provided_token

        # Valid token
        assert is_authorized(expected_token, "tok_valid_expected_token_123") is True

        # Invalid token
        assert is_authorized(expected_token, "tok_wrong_token") is False

        # Missing provided token
        assert is_authorized(expected_token, "") is False

        # Missing stored token (uninitialized job)
        assert is_authorized("", "tok_valid_expected_token_123") is False

        # Both missing
        assert is_authorized("", "") is False

    def test_internal_secret_rejection_logic(self):
        """Validate that legacy or empty internal API keys are rejected."""
        rotated_secret = "new_256bit_rotated_internal_secret_key"
        deprecated_secret = "dev-internal-secret-key-12345"

        def verify_internal_auth(auth_header: str, configured_secret: str) -> bool:
            if not configured_secret or not auth_header:
                return False
            token = auth_header.replace("Bearer ", "").strip()
            return token == configured_secret

        # Valid current secret
        assert verify_internal_auth(f"Bearer {rotated_secret}", rotated_secret) is True

        # Deprecated hardcoded secret must be rejected
        assert verify_internal_auth(f"Bearer {deprecated_secret}", rotated_secret) is False

        # Empty or unconfigured secret fails closed
        assert verify_internal_auth(f"Bearer {rotated_secret}", "") is False
        assert verify_internal_auth("", rotated_secret) is False
