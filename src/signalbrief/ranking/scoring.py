"""Multi-factor development ranking consolidating relevance, recency, and novelty."""

import math
import re
from datetime import datetime
from typing import List, Optional, Set

from signalbrief.ranking.novelty import compute_novelty_score, compute_recency_score
from signalbrief.ranking.relevance import compute_relevance_score

IMPACT_FINANCIAL_PATTERN = re.compile(
    r"(\$[\d,]+(?:\.\d+)?\s*(?:billion|million|trillion|b|m)\b|\b\d+(?:\.\d+)?\s*(?:billion|million)\s*(?:dollars|euro|usd)\b)",
    re.IGNORECASE,
)
IMPACT_REGULATORY_PATTERN = re.compile(
    r"\b(tariff|tariffs|sanction|sanctions|antitrust|ruling|mandate|compliance|investigation|lawsuit|ban|banned|subsidies|subsidy|chips act|export control)\b",
    re.IGNORECASE,
)
IMPACT_OPERATIONAL_PATTERN = re.compile(
    r"\b(acquisition|acquired|merger|plant|gigafactory|breakthrough|expansion|restructure|shutdown|deployment|deploying|commercialize)\b",
    re.IGNORECASE,
)


def compute_impact_score(cluster: dict) -> float:
    """Compute business impact score based on capital size, regulatory urgency, and operational magnitude."""
    member_titles = [m.get("title", "") for m in cluster.get("member_articles", [])]
    all_text = " ".join([
        cluster.get("centroid_title", ""),
        " ".join(cluster.get("top_keywords", [])),
        " ".join(member_titles),
    ])

    score = 0.4  # baseline

    if IMPACT_FINANCIAL_PATTERN.search(all_text):
        score += 0.3
    if IMPACT_REGULATORY_PATTERN.search(all_text):
        score += 0.2
    if IMPACT_OPERATIONAL_PATTERN.search(all_text):
        score += 0.1

    return round(min(1.0, score), 3)


def rank_developments(
    clusters: List[dict],
    domain_keywords: List[str],
    domain_subtopics: List[str],
    max_developments: int = 5,
    historical_tokens: Optional[Set[str]] = None,
) -> List[dict]:
    """Score each cluster on relevance, recency, size, impact, and multi-source credibility.

    Ranking Formula:
        Composite = (0.30 * Relevance + 0.20 * Recency + 0.20 * MultiSourceBoost + 0.15 * Impact + 0.15 * VolumeScale) * Novelty
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

        # Strategic business impact score
        impact_score = compute_impact_score(c)

        base_score = (
            0.30 * relevance +
            0.20 * avg_recency +
            0.20 * multisource_boost +
            0.15 * impact_score +
            0.15 * volume_scale
        )

        # Novelty factor
        cluster_tokens = set(c.get("top_keywords", []))
        novelty = compute_novelty_score(cluster_tokens, historical_tokens or set())
        composite_score = round(base_score * novelty, 3)

        scored.append({
            **c,
            "relevance_score": relevance,
            "recency_score": round(avg_recency, 3),
            "multisource_boost": multisource_boost,
            "volume_scale": round(volume_scale, 3),
            "impact_score": impact_score,
            "novelty_score": novelty,
            "composite_score": composite_score,
        })

    # Sort descending by composite score
    scored_sorted = sorted(scored, key=lambda x: x["composite_score"], reverse=True)
    return scored_sorted[:max_developments]
