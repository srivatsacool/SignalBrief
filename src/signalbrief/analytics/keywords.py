"""Keyword and n-gram extraction utilities for text analytics."""

import re
from collections import Counter
from typing import List, Set, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer


def extract_keywords_tfidf(
    corpus: List[str],
    top_n: int = 10,
    ngram_range: Tuple[int, int] = (1, 2),
    min_df: int = 1,
) -> List[Tuple[str, float]]:
    """Extract top salient terms from corpus using TF-IDF aggregate scoring."""
    if not corpus:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=0.95,
    )
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return []

    feature_names = vectorizer.get_feature_names_out()
    mean_scores = tfidf_matrix.mean(axis=0).A1
    scored_terms = sorted(zip(feature_names, mean_scores), key=lambda x: x[1], reverse=True)
    return scored_terms[:top_n]


def match_domain_keywords(text: str, domain_keywords: List[str]) -> List[str]:
    """Find all matching domain keywords present in text."""
    lower_text = text.lower()
    matches: Set[str] = set()
    for kw in domain_keywords:
        kw_clean = kw.strip().lower()
        if not kw_clean:
            continue
        pattern = r"\b" + re.escape(kw_clean) + r"\b"
        if re.search(pattern, lower_text):
            matches.add(kw)
    return sorted(list(matches))


def extract_ngrams(text: str, n: int = 2, top_k: int = 10) -> List[Tuple[str, int]]:
    """Extract top frequent n-grams from a document."""
    tokens = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    if len(tokens) < n:
        return []

    ngrams = [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
    counts = Counter(ngrams)
    return counts.most_common(top_k)


def compute_keyword_density(text: str, keywords: List[str]) -> float:
    """Compute the density ratio of domain keywords relative to total word count."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    if not tokens:
        return 0.0
    matches = match_domain_keywords(text, keywords)
    return len(matches) / (len(tokens) / 50.0)
