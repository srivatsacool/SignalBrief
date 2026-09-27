"""URL normalization and content deduplication functions."""

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def normalize_url(raw_url: str) -> str:
    """Normalize URLs by stripping tracking queries (utm_*, ref, etc.) and fragment."""
    parsed = urlparse(raw_url.strip())
    # Filter tracking parameters
    query_params = parse_qsl(parsed.query)
    clean_params = [
        (k, v) for k, v in query_params
        if not k.startswith("utm_") and k not in {"ref", "fbclid", "gclid"}
    ]
    clean_query = urlencode(clean_params)
    # Lowercase scheme and netloc, remove trailing slash
    path = parsed.path.rstrip("/")
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", clean_query, ""))


def compute_content_hash(text: str) -> str:
    """Compute deterministic SHA-256 hash of normalized text."""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
