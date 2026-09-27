"""Analytics modules for SignalBrief."""

from signalbrief.analytics.classification import classify_subtopic
from signalbrief.analytics.clustering import cluster_articles
from signalbrief.analytics.embeddings import (
    TextEmbedder,
    compute_similarity_matrix,
    find_most_similar,
)
from signalbrief.analytics.entities import extract_entities
from signalbrief.analytics.keywords import (
    compute_keyword_density,
    extract_keywords_tfidf,
    extract_ngrams,
    match_domain_keywords,
)
from signalbrief.analytics.sentiment import analyze_sentiment
from signalbrief.analytics.trends import compute_publication_velocity, detect_emerging_topics

__all__ = [
    "classify_subtopic",
    "cluster_articles",
    "extract_entities",
    "analyze_sentiment",
    "extract_keywords_tfidf",
    "match_domain_keywords",
    "extract_ngrams",
    "compute_keyword_density",
    "TextEmbedder",
    "compute_similarity_matrix",
    "find_most_similar",
    "compute_publication_velocity",
    "detect_emerging_topics",
]
