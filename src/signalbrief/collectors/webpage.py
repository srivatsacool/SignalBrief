"""Direct webpage scraper for collecting articles when RSS is unavailable."""

import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from signalbrief.collectors.base import RawArticle
from signalbrief.collectors.deduplication import compute_content_hash, normalize_url

logger = logging.getLogger(__name__)


def fetch_webpage_article(
    url: str,
    source_id: str,
    domain_id: str,
    timeout_seconds: int = 15,
) -> Optional[RawArticle]:
    """Fetch and parse an individual webpage into a RawArticle."""
    headers = {
        "User-Agent": "SignalBrief/1.0 (+https://signalbrief.local; bot)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    norm_url = normalize_url(url)

    try:
        resp = requests.get(url, headers=headers, timeout=timeout_seconds)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch webpage '{url}': {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract Title
    title = None
    meta_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
    if meta_title and meta_title.get("content"):
        title = meta_title["content"].strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)

    if not title:
        return None

    # Extract Author
    author = None
    meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
    if meta_author and meta_author.get("content"):
        author = meta_author["content"].strip()

    # Extract Published Date
    published_at = None
    meta_time = (
        soup.find("meta", property="article:published_time")
        or soup.find("time", attrs={"datetime": True})
        or soup.find("meta", attrs={"name": "pubdate"})
    )
    if meta_time:
        raw_time = meta_time.get("content") or meta_time.get("datetime")
        if raw_time:
            try:
                published_at = date_parser.parse(str(raw_time))
                if published_at.tzinfo is None:
                    published_at = published_at.replace(tzinfo=timezone.utc)
            except Exception:
                published_at = None

    # Extract Content/Summary
    article_tag = soup.find("article") or soup.find("main") or soup.find("div", class_="content")
    if article_tag:
        # Strip script, style, nav, footer
        for tag in article_tag.find_all(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()
        paragraphs = [p.get_text(strip=True) for p in article_tag.find_all("p") if len(p.get_text(strip=True)) > 20]
        content_raw = "\n\n".join(paragraphs)
    else:
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 20]
        content_raw = "\n\n".join(paragraphs[:10])

    summary_raw = paragraphs[0] if paragraphs else ""
    content_hash = compute_content_hash(f"{title} {summary_raw}")

    parsed = urlparse(norm_url)
    slug = parsed.path.rstrip("/").split("/")[-1] or "page"
    article_id = f"{source_id}_{slug[:40]}_{content_hash[:8]}"

    return RawArticle(
        id=article_id,
        source_id=source_id,
        domain_id=domain_id,
        title=title,
        url=url,
        url_canonical=norm_url,
        content_hash=content_hash,
        author=author,
        published_at=published_at,
        fetched_at=datetime.now(timezone.utc),
        summary_raw=summary_raw or None,
        content_raw=content_raw or None,
    )
