"""Sentiment and tone analysis tailored for industrial and manufacturing news."""

import re
from typing import Tuple

POSITIVE_INDICATORS = {
    "award", "awards", "awarded", "grant", "grants", "funding", "invest", "investment",
    "investments", "expansion", "expand", "breakthrough", "upgrade", "upgrades", "growth",
    "advance", "advances", "advancements", "boost", "boosts", "accelerate", "accelerates",
    "partnership", "success", "adopt", "adoption", "modernize", "modernization", "innovation",
    "innovative", "deployed", "deploy", "surging", "efficient", "efficiency", "record",
    "profit", "profits", "development", "developments"
}

NEGATIVE_INDICATORS = {
    "delay", "delays", "disruption", "disruptions", "failure", "failures", "layoff", "layoffs",
    "decline", "declines", "shortage", "shortages", "bottleneck", "bottlenecks", "hazard",
    "hazards", "defect", "defects", "strike", "strikes", "breach", "cyberattack",
    "vulnerability", "vulnerabilities", "loss", "losses", "cut", "cuts", "down", "warns",
    "warning", "breakdown", "fatal", "shutdown"
}


def analyze_sentiment(text: str) -> Tuple[str, float]:
    """Analyze sentiment of industrial text.

    Returns (sentiment_label, polarity_score) where label is 'positive', 'neutral', or 'negative'
    and polarity_score is in [-1.0, 1.0].
    """
    text_lower = text.lower()
    words = set(re.findall(r"\b[a-zA-Z]+\b", text_lower))

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
