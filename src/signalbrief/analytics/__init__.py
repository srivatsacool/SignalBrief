"""Analytics module for NLP, subtopic classification, entities, and sentiment."""

from signalbrief.analytics.classification import DEFAULT_SUBTOPIC_TAXONOMY, classify_subtopic
from signalbrief.analytics.clustering import cluster_articles
from signalbrief.analytics.entities import extract_entities
from signalbrief.analytics.sentiment import analyze_sentiment

__all__ = [
    "classify_subtopic",
    "cluster_articles",
    "extract_entities",
    "analyze_sentiment",
    "DEFAULT_SUBTOPIC_TAXONOMY",
]
