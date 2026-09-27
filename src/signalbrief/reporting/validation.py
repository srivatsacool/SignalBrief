"""Editorial and quality validation for generated daily intelligence reports."""

from typing import List, Tuple
from urllib.parse import urlparse

from signalbrief.reporting.report_schema import DailyReport


def validate_report(report: DailyReport) -> Tuple[bool, List[str]]:
    """Validate that a DailyReport meets all editorial invariants and QA standards.

    Invariants:
    1. Must contain at least 1 development.
    2. Executive takeaway must be non-empty and substantive.
    3. Every development must have non-empty triadic sections ('what_changed', 'why_it_matters', 'what_to_watch').
    4. 100% Citation Coverage: Every development must have at least one valid source link.
    5. Word count and length bounds.
    """
    issues: List[str] = []

    # Invariant 1: Development count
    if not report.developments:
        issues.append("Report has 0 developments (at least 1 required).")

    # Invariant 2: Executive takeaway
    if not report.executive_takeaway or len(report.executive_takeaway.strip()) < 30:
        issues.append("Executive takeaway is missing or too brief (<30 characters).")

    # Invariant 3, 4, 5: Each development check
    for idx, dev in enumerate(report.developments, 1):
        if not dev.title or len(dev.title.strip()) < 5:
            issues.append(f"Development #{idx} has an empty or invalid title.")

        if not dev.what_changed or len(dev.what_changed.strip()) < 20:
            issues.append(f"Development #{idx} 'what_changed' is too brief (<20 characters).")

        if not dev.why_it_matters or len(dev.why_it_matters.strip()) < 20:
            issues.append(f"Development #{idx} 'why_it_matters' is too brief (<20 characters).")

        if not dev.what_to_watch or len(dev.what_to_watch.strip()) < 20:
            issues.append(f"Development #{idx} 'what_to_watch' is too brief (<20 characters).")

        # Citation validation
        if not dev.sources:
            issues.append(f"Development #{idx} has 0 sources (100% citation coverage required).")
        else:
            for s_idx, src in enumerate(dev.sources, 1):
                url = src.url if hasattr(src, "url") else (src.get("url", "") if isinstance(src, dict) else "")
                parsed = urlparse(str(url))
                if not parsed.scheme or not parsed.netloc:
                    issues.append(f"Development #{idx} source #{s_idx} has invalid URL: '{url}'")


    is_valid = len(issues) == 0
    return is_valid, issues
