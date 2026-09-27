"""Scheduling utilities for periodic source polling."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from signalbrief.config.schema import SourceConfig


def is_source_due(
    source: SourceConfig,
    last_polled_at: Optional[datetime] = None,
    now: Optional[datetime] = None,
) -> bool:
    """Determine if a source is due for polling based on its configured frequency."""
    if not source.active:
        return False

    current_time = now or datetime.now(timezone.utc)
    if last_polled_at is None:
        return True

    if last_polled_at.tzinfo is None:
        last_polled_at = last_polled_at.replace(tzinfo=timezone.utc)

    interval = timedelta(minutes=source.polling_frequency_minutes)
    return (current_time - last_polled_at) >= interval


def filter_due_sources(
    sources: List[SourceConfig],
    last_poll_timestamps: Dict[str, Optional[datetime]],
    now: Optional[datetime] = None,
) -> List[SourceConfig]:
    """Filter a list of sources down to those currently due for polling."""
    return [
        src for src in sources
        if is_source_due(src, last_poll_timestamps.get(src.id), now=now)
    ]
