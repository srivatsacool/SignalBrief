"""Topic clustering using TF-IDF vectorization and agglomerative linkage."""

from typing import Dict, List, Tuple

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from signalbrief.preprocessing.cleaning import JOURNALISTIC_STOPWORDS


def cluster_articles(
    articles: List[dict],
    n_clusters: int = 6,
    max_features: int = 500,
) -> Tuple[List[dict], Dict[int, dict]]:
    """Cluster articles into thematic groups using TF-IDF and Agglomerative Clustering.

    Returns:
        (annotated_articles_with_cluster_id, cluster_metadata_dict)
    """
    if len(articles) < n_clusters:
        n_clusters = max(1, len(articles))

    texts = [f"{a['title']} {a.get('clean_text', '')}" for a in articles]
    custom_stop_words = list(ENGLISH_STOP_WORDS.union(JOURNALISTIC_STOPWORDS))
    vectorizer = TfidfVectorizer(
        stop_words=custom_stop_words,
        max_features=max_features,
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Perform clustering
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric="cosine",
        linkage="average",
    )
    cluster_labels = clustering.fit_predict(tfidf_matrix.toarray())

    # Build cluster metadata
    feature_names = vectorizer.get_feature_names_out()
    cluster_info = {}

    for c_id in range(n_clusters):
        member_indices = [i for i, lbl in enumerate(cluster_labels) if lbl == c_id]
        if not member_indices:
            continue

        member_matrix = tfidf_matrix[member_indices].toarray()
        mean_vector = member_matrix.mean(axis=0)

        # Top keywords for cluster (excluding journalistic noise)
        top_keyword_indices = mean_vector.argsort()[-12:][::-1]
        raw_keywords = [feature_names[idx] for idx in top_keyword_indices if mean_vector[idx] > 0]
        top_keywords = [
            k for k in raw_keywords
            if not any(stop in k.lower().split() for stop in JOURNALISTIC_STOPWORDS)
            and len(k) > 2
        ][:6]

        # Find centroid (article closest to cluster mean vector)
        similarities = cosine_similarity(member_matrix, mean_vector.reshape(1, -1))
        centroid_idx = member_indices[np.argmax(similarities)]
        centroid_article = articles[centroid_idx]

        member_articles = [articles[i] for i in member_indices]
        sources = list(set(a.get("source_id", "source") for a in member_articles))

        # Format clean, readable theme label
        if top_keywords:
            theme_label = " & ".join(k.title() for k in top_keywords[:3])
        else:
            theme_label = f"Theme {c_id}"

        cluster_info[c_id] = {
            "cluster_id": c_id,
            "size": len(member_indices),
            "top_keywords": top_keywords,
            "theme_label": theme_label,
            "sources": sources,
            "is_multisource": len(sources) > 1,
            "centroid_article_id": centroid_article.get("id", f"art_{centroid_idx}"),
            "centroid_title": centroid_article.get("title", ""),
            "centroid_url": centroid_article.get("url") or centroid_article.get("url_canonical", ""),
            "member_articles": member_articles,
        }


    # Annotate articles with cluster ID
    annotated = []
    for i, a in enumerate(articles):
        c_id = int(cluster_labels[i])
        record = dict(a)
        record["cluster_id"] = c_id
        record["cluster_theme"] = cluster_info[c_id]["theme_label"]
        annotated.append(record)

    return annotated, cluster_info
