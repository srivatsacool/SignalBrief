"""API collector for fetching articles from JSON REST endpoints."""

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import requests
from dateutil import parser as date_parser

from signalbrief.collectors.base import RawArticle
from signalbrief.collectors.deduplication import compute_content_hash, normalize_url
from signalbrief.config.schema import SourceConfig

logger = logging.getLogger(__name__)


def default_json_mapper(item: Dict[str, Any], source: SourceConfig) -> Optional[RawArticle]:
    """Default mapper to convert generic JSON objects into RawArticle."""
    url = item.get("url") or item.get("link") or item.get("web_url")
    title = item.get("title") or item.get("headline")
    if not url or not title:
        return None

    norm_url = normalize_url(str(url))
    summary = item.get("summary") or item.get("description") or item.get("abstract") or ""
    content = item.get("content") or item.get("body") or summary

    pub_date_val = item.get("published_at") or item.get("published") or item.get("pub_date") or item.get("created_at")
    published_at = None
    if pub_date_val:
        try:
            published_at = date_parser.parse(str(pub_date_val))
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
        except Exception:
            published_at = None

    content_hash = compute_content_hash(f"{title} {summary}")
    parsed = urlparse(norm_url)
    slug = parsed.path.rstrip("/").split("/")[-1] or "item"
    article_id = f"{source.id}_{slug[:40]}_{content_hash[:8]}"

    return RawArticle(
        id=article_id,
        source_id=source.id,
        domain_id=source.id.split("_")[0],
        title=str(title).strip(),
        url=str(url),
        url_canonical=norm_url,
        content_hash=content_hash,
        author=item.get("author") or item.get("byline"),
        published_at=published_at,
        fetched_at=datetime.now(timezone.utc),
        summary_raw=str(summary).strip() if summary else None,
        content_raw=str(content).strip() if content else None,
    )


def fetch_api_articles(
    source: SourceConfig,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    mapper: Optional[Callable[[Dict[str, Any], SourceConfig], Optional[RawArticle]]] = None,
    max_articles: int = 50,
    timeout_seconds: int = 15,
) -> List[RawArticle]:
    """Fetch articles from a JSON API endpoint."""
    if not source.endpoint:
        logger.warning(f"No endpoint defined for API source: {source.id}")
        return []

    req_headers = {"User-Agent": "SignalBrief/1.0 (+https://signalbrief.local)"}
    if headers:
        req_headers.update(headers)

    articles: List[RawArticle] = []
    item_mapper = mapper or default_json_mapper

    try:
        resp = requests.get(source.endpoint, headers=req_headers, params=params, timeout=timeout_seconds)
        resp.raise_for_status()
        data = resp.json()

        # Handle various response envelope structures
        raw_items: List[Dict[str, Any]] = []
        if isinstance(data, list):
            raw_items = data
        elif isinstance(data, dict):
            for key in ["articles", "items", "results", "data", "posts"]:
                if key in data and isinstance(data[key], list):
                    raw_items = data[key]
                    break
            if not raw_items:
                raw_items = [data]

        for item in raw_items[:max_articles]:
            if isinstance(item, dict):
                art = item_mapper(item, source)
                if art:
                    articles.append(art)

    except Exception as e:
        logger.error(f"Error fetching from API source '{source.id}': {e}")

    return articles
