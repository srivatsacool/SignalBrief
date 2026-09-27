"""Temporal trend, velocity, and emerging theme detection utilities."""

from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


def compute_publication_velocity(
    articles: List[Dict[str, Any]],
    date_field: str = "published_at",
    freq: str = "D",
) -> Dict[str, int]:
    """Compute article volume over time intervals."""
    dates = []
    for art in articles:
        dt_val = art.get(date_field)
        if dt_val:
            if isinstance(dt_val, str):
                try:
                    dt = pd.to_datetime(dt_val, utc=True)
                    dates.append(dt)
                except Exception:
                    pass
            elif isinstance(dt_val, datetime):
                dates.append(dt_val)

    if not dates:
        return {}

    ts_series = pd.Series(1, index=pd.DatetimeIndex(dates))
    resampled = ts_series.resample(freq).sum()
    return {k.strftime("%Y-%m-%d"): int(v) for k, v in resampled.items()}


def detect_emerging_topics(
    recent_articles: List[Dict[str, Any]],
    baseline_articles: Optional[List[Dict[str, Any]]] = None,
    topic_field: str = "subtopic",
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Detect topics exhibiting highest growth or momentum relative to baseline."""
    recent_counts = Counter(art.get(topic_field, "general") for art in recent_articles)
    total_recent = sum(recent_counts.values()) or 1

    baseline_counts = Counter()
    if baseline_articles:
        baseline_counts = Counter(art.get(topic_field, "general") for art in baseline_articles)
    total_baseline = sum(baseline_counts.values()) or 1

    emerging = []
    for topic, r_count in recent_counts.items():
        r_share = r_count / total_recent
        b_share = baseline_counts.get(topic, 0) / total_baseline
        velocity = (r_share - b_share) / (b_share + 0.05)
        emerging.append({
            "topic": topic,
            "recent_count": r_count,
            "recent_share": round(r_share, 3),
            "velocity_score": round(float(velocity), 3),
        })

    emerging.sort(key=lambda x: x["velocity_score"], reverse=True)
    return emerging[:top_k]
