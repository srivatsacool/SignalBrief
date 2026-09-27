"""Sentiment and tone analysis tailored for industrial and manufacturing news."""

from typing import Tuple

POSITIVE_INDICATORS = {
    "award", "awards", "grant", "funding", "invest", "investment", "investments",
    "expansion", "expand", "breakthrough", "upgrade", "upgrades", "growth",
    "advance", "advances", "boost", "accelerate", "partnership", "success",
    "adopt", "adoption", "modernize", "innovation", "innovative"
}

NEGATIVE_INDICATORS = {
    "delay", "delays", "disruption", "disruptions", "failure", "layoff", "layoffs",
    "decline", "shortage", "shortages", "bottleneck", "bottlenecks", "hazard",
    "defect", "defects", "strike", "breach", "cyberattack", "vulnerability",
    "loss", "losses", "cut", "cuts", "down"
}


def analyze_sentiment(text: str) -> Tuple[str, float]:
    """Analyze sentiment of industrial text.

    Returns (sentiment_label, polarity_score) where label is 'positive', 'neutral', or 'negative'
    and polarity_score is in [-1.0, 1.0].
    """
    text_lower = text.lower()
    words = set(text_lower.split())

    pos_matches = len(words.intersection(POSITIVE_INDICATORS))
    neg_matches = len(words.intersection(NEGATIVE_INDICATORS))

    total = pos_matches + neg_matches
    if total == 0:
        return "neutral", 0.0

    polarity = (pos_matches - neg_matches) / total
    polarity = round(polarity, 2)

    if polarity > 0.15:
        return "positive", polarity
    elif polarity < -0.15:
        return "negative", polarity
    else:
        return "neutral", polarity
