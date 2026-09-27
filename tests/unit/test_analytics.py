"""Unit tests for NLP classification, NER, sentiment, clustering, embeddings, and trends."""

from signalbrief.analytics.classification import classify_subtopic
from signalbrief.analytics.clustering import cluster_articles
from signalbrief.analytics.embeddings import (
    TextEmbedder,
    compute_similarity_matrix,
    find_most_similar,
)
from signalbrief.analytics.entities import extract_entities
from signalbrief.analytics.keywords import (
    extract_keywords_tfidf,
    extract_ngrams,
    match_domain_keywords,
)
from signalbrief.analytics.sentiment import analyze_sentiment
from signalbrief.analytics.trends import compute_publication_velocity, detect_emerging_topics


def test_subtopic_classification():
    """Verify subtopic classification across standard categories."""
    ai_text = "Generative AI and computer vision inspect factory defect rates with machine learning."
    subtopic, conf = classify_subtopic(ai_text)
    assert subtopic.lower() == "industrial ai"
    assert conf > 0.0

    chain_text = "Port congestion, logistics shipping delays, and warehouse supply chain bottlenecks."
    subtopic2, _ = classify_subtopic(chain_text)
    assert subtopic2.lower() == "supply chain resilience"



def test_named_entity_extraction():
    """Verify entity recognition pulls organizations, agencies, and tech terms."""
    sample = "NIST announced that Amazon and US Steel deployed new robotics systems."
    entities = extract_entities(sample)
    assert "NIST" in entities.get("organizations", []) or "NIST" in entities.get("agencies", [])
    assert any("Robotics" in t for t in entities.get("technologies", []))


def test_sentiment_analysis():
    """Verify industrial sentiment scoring."""
    pos_text = "The manufacturer reported record expansion, surging efficiency, and robust profit growth."
    label_pos, score_pos = analyze_sentiment(pos_text)
    assert label_pos == "positive"
    assert score_pos > 0.1

    neg_text = "Severe breakdown, acute equipment failure, fatal defect, and shutdown."
    label_neg, score_neg = analyze_sentiment(neg_text)
    assert label_neg == "negative"
    assert score_neg < -0.1


def test_keywords_and_ngrams():
    """Verify TF-IDF keyword extraction, domain keyword matching, and bigrams."""
    corpus = [
        "Robotics automation accelerates industrial assembly plant throughput.",
        "Industrial automation transforms factory lines with advanced robotics.",
        "Robotics suppliers expand warehouse automated vehicle lines.",
    ]
    salient = extract_keywords_tfidf(corpus, top_n=3)
    assert len(salient) > 0

    matched = match_domain_keywords(corpus[0], ["robotics", "automation", "cybersecurity"])
    assert "robotics" in matched
    assert "automation" in matched
    assert "cybersecurity" not in matched

    ngrams = extract_ngrams(corpus[0], n=2, top_k=5)
    assert len(ngrams) > 0


def test_text_embedder_and_similarity():
    """Verify TextEmbedder and cosine similarity matrix."""
    corpus = [
        "autonomous mobile robots in logistics warehouse",
        "self-driving vehicles and robots in distribution centers",
        "pharmaceutical chemistry clinical trial results",
    ]
    embedder = TextEmbedder(max_features=50)
    matrix = embedder.fit_transform(corpus)
    assert matrix.shape[0] == 3

    sims = compute_similarity_matrix(matrix)
    # Corpus 0 and 1 should have much higher similarity than 0 and 2
    assert sims[0, 1] > sims[0, 2]

    similar = find_most_similar(matrix[0], matrix, top_k=2)
    assert similar[0][0] == 0  # self is most similar


def test_topic_clustering():
    """Verify agglomerative clustering partitions articles and finds centroids."""
    articles = [
        {"id": "a1", "title": "Robotics in automotive plants", "clean_text": "Robots weld vehicle chassis in smart factory.", "source_id": "s1"},
        {"id": "a2", "title": "Automated mobile robots in warehouse", "clean_text": "Industrial robots move freight pallets.", "source_id": "s2"},
        {"id": "a3", "title": "Federal manufacturing grants announced", "clean_text": "NIST awards grants for clean energy production.", "source_id": "s1"},
        {"id": "a4", "title": "Government subsidies for semiconductor fabs", "clean_text": "Federal funding accelerates chip fabrication.", "source_id": "s2"},
    ]
    annotated, clusters = cluster_articles(articles, n_clusters=2)
    assert len(annotated) == 4
    assert len(clusters) == 2
    for c in clusters.values():
        assert "centroid_title" in c
        assert "member_articles" in c
        assert len(c["member_articles"]) > 0


def test_trends_and_velocity():
    """Verify temporal velocity and emerging topic calculations."""
    articles = [
        {"published_at": "2026-09-27T10:00:00Z", "subtopic": "industrial_ai"},
        {"published_at": "2026-09-27T14:00:00Z", "subtopic": "industrial_ai"},
        {"published_at": "2026-09-28T09:00:00Z", "subtopic": "industrial_ai"},
        {"published_at": "2026-09-28T11:00:00Z", "subtopic": "supply_chain"},
    ]
    velocity = compute_publication_velocity(articles, freq="D")
    assert "2026-09-27" in velocity
    assert "2026-09-28" in velocity

    emerging = detect_emerging_topics(articles[:2], articles[2:], top_k=2)
    assert len(emerging) > 0
