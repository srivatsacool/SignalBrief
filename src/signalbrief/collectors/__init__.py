"""Collector modules for SignalBrief."""

from signalbrief.collectors.api import fetch_api_articles
from signalbrief.collectors.base import RawArticle
from signalbrief.collectors.deduplication import compute_content_hash, normalize_url
from signalbrief.collectors.rss import fetch_rss_feed
from signalbrief.collectors.scheduler import filter_due_sources, is_source_due
from signalbrief.collectors.webpage import fetch_webpage_article

__all__ = [
    "RawArticle",
    "fetch_rss_feed",
    "fetch_api_articles",
    "fetch_webpage_article",
    "normalize_url",
    "compute_content_hash",
    "is_source_due",
    "filter_due_sources",
]
