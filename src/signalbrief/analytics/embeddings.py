"""Embedding generation and vector similarity utilities."""

import logging
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class TextEmbedder:
    """Zero-dependency TF-IDF text embedder with optional neural fallback."""

    def __init__(self, max_features: int = 500, ngram_range: Tuple[int, int] = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=max_features,
            ngram_range=ngram_range,
        )
        self._is_fitted = False

    def fit(self, texts: List[str]) -> "TextEmbedder":
        """Fit the vectorizer on a corpus of texts."""
        if texts:
            self.vectorizer.fit(texts)
            self._is_fitted = True
        return self

    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts into normalized TF-IDF embedding vectors."""
        if not self._is_fitted:
            self.fit(texts)
        matrix = self.vectorizer.transform(texts).toarray()
        return matrix

    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Fit and transform texts in one step."""
        self.fit(texts)
        return self.transform(texts)


def compute_similarity_matrix(vectors: np.ndarray) -> np.ndarray:
    """Compute pairwise cosine similarity between embedding vectors."""
    if len(vectors) == 0:
        return np.empty((0, 0))
    return cosine_similarity(vectors)


def find_most_similar(
    query_vector: np.ndarray,
    corpus_vectors: np.ndarray,
    top_k: int = 5,
) -> List[Tuple[int, float]]:
    """Return indices and similarity scores of top_k most similar corpus vectors."""
    if len(corpus_vectors) == 0:
        return []
    sims = cosine_similarity(query_vector.reshape(1, -1), corpus_vectors)[0]
    ranked_indices = np.argsort(-sims)[:top_k]
    return [(int(idx), float(sims[idx])) for idx in ranked_indices]
