"""Unit tests for collectors, deduplication, API fetcher, and scheduling."""

from datetime import datetime, timedelta, timezone

from signalbrief.collectors.api import default_json_mapper
from signalbrief.collectors.base import RawArticle
from signalbrief.collectors.deduplication import compute_content_hash, normalize_url
from signalbrief.collectors.scheduler import filter_due_sources, is_source_due
from signalbrief.config.schema import SourceConfig


def test_url_normalization():
    """Verify UTM parameters and fragments are stripped from URLs."""
    dirty_url = "https://WWW.Example.com/News/Article/?utm_source=twitter&utm_medium=social&ref=sidebar#top"
    clean_url = normalize_url(dirty_url)
    assert clean_url == "https://www.example.com/News/Article"



def test_content_hash_deterministic():
    """Verify SHA-256 hash is deterministic and whitespace-insensitive."""
    t1 = "Manufacturing automated assembly line expands."
    t2 = "  manufacturing   automated  assembly line  expands.  "
    h1 = compute_content_hash(t1)
    h2 = compute_content_hash(t2)
    assert h1 == h2
    assert len(h1) == 64


def test_api_mapper_valid():
    """Verify default JSON mapper maps items to RawArticle correctly."""
    source = SourceConfig(
        id="test_api_src",
        name="Test API Source",
        domain_id="manufacturing",
        url="https://api.example.com",
        feed_url="https://api.example.com/items.json",
    )
    item = {
        "title": "Robotics deployment in gigafactory",
        "url": "https://api.example.com/posts/robotics-deployment?utm_campaign=feed",
        "summary": "Full autonomous robot arm rollouts have been approved.",
        "published_at": "2026-09-28T02:00:00Z",
    }
    art = default_json_mapper(item, source)
    assert art is not None
    assert isinstance(art, RawArticle)
    assert art.source_id == "test_api_src"
    assert "robotics deployment" in art.title.lower()
    assert art.url_canonical == "https://api.example.com/posts/robotics-deployment"
    assert art.published_at is not None


def test_scheduler_is_due():
    """Verify polling interval logic."""
    source = SourceConfig(
        id="src1",
        name="Source 1",
        domain_id="manufacturing",
        url="https://example.com",
        feed_url="https://example.com/feed",
        polling_frequency_minutes=60,
        active=True,
    )
    now = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)

    # Never polled before -> should be due
    assert is_source_due(source, last_polled_at=None, now=now) is True

    # Polled 30 mins ago -> not due
    last_poll_recent = now - timedelta(minutes=30)
    assert is_source_due(source, last_polled_at=last_poll_recent, now=now) is False

    # Polled 75 mins ago -> due
    last_poll_past = now - timedelta(minutes=75)
    assert is_source_due(source, last_polled_at=last_poll_past, now=now) is True

    # Inactive source -> never due
    inactive_src = source.model_copy(update={"active": False})
    assert is_source_due(inactive_src, last_polled_at=None, now=now) is False


def test_scheduler_filter_due_sources():
    """Verify filtering list of sources based on poll timestamps."""
    now = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    s1 = SourceConfig(id="s1", name="S1", domain_id="mfg", url="http://s1", feed_url="http://s1/f", polling_frequency_minutes=60)
    s2 = SourceConfig(id="s2", name="S2", domain_id="mfg", url="http://s2", feed_url="http://s2/f", polling_frequency_minutes=120)

    timestamps = {
        "s1": now - timedelta(minutes=90),  # due (60m)
        "s2": now - timedelta(minutes=30),  # not due (120m)
    }
    due = filter_due_sources([s1, s2], timestamps, now=now)
    assert len(due) == 1
    assert due[0].id == "s1"
