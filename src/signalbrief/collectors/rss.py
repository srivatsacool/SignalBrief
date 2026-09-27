"""RSS/Atom feed collector with date parsing and deduplication."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import feedparser
from dateutil import parser as date_parser

from signalbrief.collectors.base import RawArticle
from signalbrief.collectors.deduplication import compute_content_hash, normalize_url
from signalbrief.config.schema import SourceConfig

logger = logging.getLogger(__name__)


def parse_entry_date(entry: dict) -> Optional[datetime]:
    """Parse published or updated date from a feedparser entry."""
    for field in ("published", "pubDate", "updated", "created"):
        val = entry.get(field)
        if val:
            try:
                dt = date_parser.parse(val)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                continue
    return None


def fetch_rss_feed(source: SourceConfig, max_articles: int = 25) -> List[RawArticle]:
    """Fetch and parse articles from an RSS/Atom feed."""
    logger.info(f"Fetching RSS feed: {source.name} ({source.feed_url})")
    parsed_feed = feedparser.parse(source.feed_url)
    articles: List[RawArticle] = []

    for entry in parsed_feed.entries[:max_articles]:
        raw_url = entry.get("link", "")
        if not raw_url:
            continue

        title = entry.get("title", "").strip()
        summary = entry.get("summary", "") or entry.get("description", "")
        canonical = normalize_url(raw_url)
        content_hash = compute_content_hash(f"{title} {summary}")
        published_at = parse_entry_date(entry)

        article = RawArticle(
            id=f"{source.id}_{content_hash[:12]}",
            source_id=source.id,
            domain_id=source.domain_id,
            title=title,
            url=raw_url,
            url_canonical=canonical,
            content_hash=content_hash,
            author=entry.get("author"),
            published_at=published_at,
            summary_raw=summary,
            content_raw=summary,
        )
        articles.append(article)

    logger.info(f"Retrieved {len(articles)} articles from {source.name}")
    return articles
