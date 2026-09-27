"""Novelty and recency decay scoring functions."""

import math
from datetime import datetime, timezone
from typing import Optional, Set


def compute_recency_score(
    published_at: Optional[datetime],
    current_time: Optional[datetime] = None,
    half_life_hours: float = 48.0,
) -> float:
    """Compute exponential recency decay score in [0.0, 1.0].

    Score drops to 0.5 after half_life_hours.
    """
    if not published_at:
        return 0.5
    now = current_time or datetime.now(timezone.utc)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)

    delta_hours = max(0.0, (now - published_at).total_seconds() / 3600.0)
    decay_lambda = math.log(2) / half_life_hours
    score = math.exp(-decay_lambda * delta_hours)
    return round(max(0.05, min(1.0, score)), 3)


def compute_novelty_score(
    item_tokens: Set[str],
    historical_tokens: Set[str],
) -> float:
    """Compute novelty penalty/score relative to historical coverage.

    Returns a multiplier in [0.2, 1.0]. Lower if mostly identical to yesterday's tokens.
    """
    if not historical_tokens or not item_tokens:
        return 1.0

    overlap = len(item_tokens.intersection(historical_tokens))
    jaccard = overlap / len(item_tokens.union(historical_tokens))
    # Penalize if jaccard overlap is very high (> 0.6)
    novelty = 1.0 - (0.8 * jaccard)
    return round(max(0.2, min(1.0, novelty)), 3)
