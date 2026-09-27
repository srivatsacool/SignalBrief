"""Topic clustering using TF-IDF vectorization and agglomerative linkage."""

from typing import Dict, List, Tuple

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
    vectorizer = TfidfVectorizer(stop_words="english", max_features=max_features, ngram_range=(1, 2))
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

        # Top keywords for cluster
        top_keyword_indices = mean_vector.argsort()[-6:][::-1]
        top_keywords = [feature_names[idx] for idx in top_keyword_indices if mean_vector[idx] > 0]

        # Find centroid (article closest to cluster mean vector)
        similarities = cosine_similarity(member_matrix, mean_vector.reshape(1, -1))
        centroid_idx = member_indices[np.argmax(similarities)]
        centroid_article = articles[centroid_idx]

        member_articles = [articles[i] for i in member_indices]
        sources = list(set(a["source_id"] for a in member_articles))

        cluster_info[c_id] = {
            "cluster_id": c_id,
            "size": len(member_indices),
            "top_keywords": top_keywords,
            "theme_label": " & ".join(top_keywords[:3]).title() if top_keywords else f"Theme {c_id}",
            "sources": sources,
            "is_multisource": len(sources) > 1,
            "centroid_article_id": centroid_article["id"],
            "centroid_title": centroid_article["title"],
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
