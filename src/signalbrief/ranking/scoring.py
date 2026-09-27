"""Multi-factor relevance, recency decay, and development scoring."""

import math
from datetime import datetime, timezone
from typing import List, Optional


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


def compute_relevance_score(
    text: str,
    keywords: List[str],
    subtopics: List[str],
) -> float:
    """Compute keyword relevance score in [0.0, 1.0]."""
    text_lower = text.lower()
    kw_hits = sum(1.5 if " " in kw else 1.0 for kw in keywords if kw.lower() in text_lower)
    sub_hits = sum(1.2 if " " in sub else 1.0 for sub in subtopics if sub.lower() in text_lower)
    raw_score = (kw_hits * 0.6) + (sub_hits * 0.4)
    # Sigmoidal scaling to [0, 1]
    scaled = 1.0 / (1.0 + math.exp(-0.8 * (raw_score - 2.0)))
    return round(float(scaled), 3)


def rank_developments(
    clusters: List[dict],
    domain_keywords: List[str],
    domain_subtopics: List[str],
    max_developments: int = 5,
) -> List[dict]:
    """Score each cluster on relevance, recency, size, and multi-source credibility.

    Ranking Formula:
        Composite = 0.35 * Relevance + 0.25 * Recency + 0.20 * MultiSourceBoost + 0.20 * VolumeScale
    """
    scored = []
    for c in clusters:
        centroid_text = f"{c.get('centroid_title', '')} {' '.join(c.get('top_keywords', []))}"
        relevance = compute_relevance_score(centroid_text, domain_keywords, domain_subtopics)

        # Average recency across member articles
        recency_scores = []
        for m in c.get("member_articles", []):
            pub_str = m.get("published_at")
            if pub_str:
                try:
                    dt = datetime.fromisoformat(pub_str)
                    recency_scores.append(compute_recency_score(dt))
                except Exception:
                    pass
        avg_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 0.5

        # Multi-source boost: 1.0 if >1 source, else 0.5
        multisource_boost = 1.0 if c.get("is_multisource") else 0.5

        # Volume scale: logarithmic saturation
        size = c.get("size", len(c.get("member_articles", [])))
        volume_scale = min(1.0, math.log(size + 1) / math.log(15))

        composite_score = (
            0.35 * relevance +
            0.25 * avg_recency +
            0.20 * multisource_boost +
            0.20 * volume_scale
        )
        composite_score = round(composite_score, 3)

        scored.append({
            **c,
            "relevance_score": relevance,
            "recency_score": round(avg_recency, 3),
            "multisource_boost": multisource_boost,
            "volume_scale": round(volume_scale, 3),
            "composite_score": composite_score,
        })

    # Sort descending by composite score
    scored_sorted = sorted(scored, key=lambda x: x["composite_score"], reverse=True)
    return scored_sorted[:max_developments]
