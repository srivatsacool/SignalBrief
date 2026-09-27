"""Unit tests for ranking, relevance, novelty, and composite scoring."""

from datetime import datetime, timedelta, timezone

from signalbrief.ranking.novelty import compute_novelty_score, compute_recency_score
from signalbrief.ranking.relevance import compute_relevance_score
from signalbrief.ranking.scoring import rank_developments


def test_relevance_score():
    """Verify relevance scoring favors matching keywords and subtopics."""
    text_relevant = "Advanced industrial robotics in smart manufacturing facilities."
    text_irrelevant = "Celebrity red carpet movie premiere review."
    keywords = ["robotics", "manufacturing", "automation"]
    subtopics = ["production_technology"]

    score_rel = compute_relevance_score(text_relevant, keywords, subtopics)
    score_irrel = compute_relevance_score(text_irrelevant, keywords, subtopics)
    assert score_rel > score_irrel
    assert 0.0 <= score_rel <= 1.0


def test_recency_decay():
    """Verify exponential recency decay formula and 48-hour half-life."""
    now = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    t_zero = now
    t_half = now - timedelta(hours=48)
    t_old = now - timedelta(hours=96)

    score_zero = compute_recency_score(t_zero, current_time=now, half_life_hours=48.0)
    score_half = compute_recency_score(t_half, current_time=now, half_life_hours=48.0)
    score_old = compute_recency_score(t_old, current_time=now, half_life_hours=48.0)

    assert score_zero == 1.0
    assert 0.48 <= score_half <= 0.52
    assert 0.20 <= score_old <= 0.30


def test_novelty_scoring():
    """Verify novelty penalizes high keyword overlap with historical runs."""
    hist = {"robotics", "automation", "manufacturing"}
    fresh = {"semiconductors", "lithography", "wafers"}
    identical = {"robotics", "automation", "manufacturing"}

    score_fresh = compute_novelty_score(fresh, hist)
    score_ident = compute_novelty_score(identical, hist)

    assert score_fresh == 1.0
    assert score_ident < 0.5


def test_rank_developments():
    """Verify composite ranking prioritizes high relevance and multi-source credibility."""
    clusters = [
        {
            "cluster_id": 0,
            "centroid_title": "Hollywood movie actor awards",
            "top_keywords": ["actor", "movie"],
            "sources": ["src1"],
            "is_multisource": False,
            "size": 1,
            "member_articles": [],
        },
        {
            "cluster_id": 1,
            "centroid_title": "Industrial robotics smart manufacturing factory rollout",
            "top_keywords": ["robotics", "manufacturing", "automation"],
            "sources": ["nist", "manufacturing_dive"],
            "is_multisource": True,
            "size": 6,
            "member_articles": [
                {"published_at": "2026-09-28T08:00:00Z"},
                {"published_at": "2026-09-28T09:00:00Z"},
            ],
        },
    ]
    ranked = rank_developments(
        clusters,
        domain_keywords=["robotics", "manufacturing"],
        domain_subtopics=["production_technology"],
        max_developments=2,
    )
    assert len(ranked) == 2
    assert ranked[0]["cluster_id"] == 1
    assert ranked[0]["composite_score"] > ranked[1]["composite_score"]
    assert ranked[0]["multisource_boost"] == 1.0
