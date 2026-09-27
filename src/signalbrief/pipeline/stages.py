"""End-to-end pipeline stages integrating collection, preprocessing, analytics, and reporting."""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

from signalbrief.analytics.classification import classify_subtopic
from signalbrief.analytics.clustering import cluster_articles
from signalbrief.analytics.entities import extract_entities
from signalbrief.analytics.sentiment import analyze_sentiment
from signalbrief.collectors.base import RawArticle
from signalbrief.collectors.deduplication import compute_content_hash, normalize_url
from signalbrief.collectors.rss import fetch_rss_feed
from signalbrief.config.schema import DomainConfig, PipelineConfig, SourceConfig
from signalbrief.preprocessing.cleaning import clean_article_text, count_words
from signalbrief.preprocessing.language import detect_language
from signalbrief.preprocessing.validation import CleanArticle
from signalbrief.ranking.scoring import rank_developments
from signalbrief.reporting.renderer import render_email_html, render_email_text, render_html_report
from signalbrief.reporting.report_schema import DailyReport
from signalbrief.reporting.summarization import build_daily_report_payload

logger = logging.getLogger(__name__)


def stage_collect(
    sources: List[SourceConfig],
    pipeline_cfg: PipelineConfig,
) -> Tuple[List[RawArticle], Dict[str, int]]:
    """Stage 1: Ingest articles from sources with deduplication."""
    articles: List[RawArticle] = []
    seen_urls = set()
    seen_hashes = set()
    stats = {"fetched": 0, "retained": 0, "url_dupes": 0, "hash_dupes": 0, "errors": 0}

    for src in sources:
        try:
            feed_items = fetch_rss_feed(
                src,
                max_articles=pipeline_cfg.collection.max_articles_per_source,
                timeout_seconds=pipeline_cfg.collection.request_timeout_seconds,
            )
            if not feed_items:
                stats["errors"] += 1
                continue
            stats["fetched"] += len(feed_items)
            for item in feed_items:
                canon_url = normalize_url(item.url)
                c_hash = compute_content_hash(f"{item.title} {item.summary_raw or ''}")
                if canon_url in seen_urls:
                    stats["url_dupes"] += 1
                    continue
                if c_hash in seen_hashes:
                    stats["hash_dupes"] += 1
                    continue
                seen_urls.add(canon_url)
                seen_hashes.add(c_hash)
                stats["retained"] += 1
                articles.append(item)
        except Exception as e:
            logger.error(f"Error collecting from {src.id}: {e}")
            stats["errors"] += 1

    return articles, stats


def stage_preprocess(
    raw_articles: List[RawArticle],
    pipeline_cfg: PipelineConfig,
) -> Tuple[List[CleanArticle], Dict[str, int]]:
    """Stage 2: Clean HTML, normalize unicode, and validate language and length."""
    clean_items: List[CleanArticle] = []
    stats = {"valid": 0, "rejected": 0}
    supported = pipeline_cfg.preprocessing.supported_languages

    for raw in raw_articles:
        raw_text = raw.content_raw or raw.summary_raw or ""
        clean_text = clean_article_text(raw_text)
        w_count = count_words(clean_text)

        detected_lang = detect_language(clean_text) if w_count >= 10 else "unknown"

        if w_count < 15 or w_count > pipeline_cfg.preprocessing.max_article_length_words:
            stats["rejected"] += 1
            continue
        if detected_lang not in supported:
            stats["rejected"] += 1
            continue

        clean_art = CleanArticle(
            id=raw.id,
            source_id=raw.source_id,
            domain_id=raw.domain_id,
            title=raw.title.strip(),
            url=raw.url,
            url_canonical=raw.url_canonical or raw.url,
            content_hash=raw.content_hash,
            author=raw.author,
            published_at=raw.published_at,
            fetched_at=raw.fetched_at,
            clean_text=clean_text,
            word_count=w_count,
            language=detected_lang,
            is_valid=True,
        )
        clean_items.append(clean_art)
        stats["valid"] += 1

    return clean_items, stats


def stage_analyze(clean_articles: List[CleanArticle]) -> List[dict]:
    """Stage 3: Annotate articles with subtopics, entities, and sentiment."""
    annotated = []
    for art in clean_articles:
        text = f"{art.title} {art.clean_text}"
        subtopic, confidence = classify_subtopic(text)
        entities = extract_entities(text)
        sentiment_label, sentiment_score = analyze_sentiment(text)

        record = art.model_dump()
        record["subtopic"] = subtopic
        record["subtopic_confidence"] = confidence
        record["entities"] = entities
        record["sentiment_label"] = sentiment_label
        record["sentiment_score"] = sentiment_score
        annotated.append(record)
    return annotated


def stage_cluster_and_rank(
    annotated_articles: List[dict],
    domain_cfg: DomainConfig,
    n_clusters: int = 6,
) -> Tuple[List[dict], Dict[int, dict]]:
    """Stage 4: Cluster articles and score/rank top developments."""
    clustered, cluster_info = cluster_articles(annotated_articles, n_clusters=n_clusters)
    ranked = rank_developments(
        list(cluster_info.values()),
        domain_keywords=domain_cfg.keywords,
        domain_subtopics=domain_cfg.subtopics,
        max_developments=domain_cfg.report.max_developments,
    )
    return ranked, cluster_info


def stage_render(
    domain_cfg: DomainConfig,
    ranked_developments: List[dict],
    total_articles: int,
    report_date: str,
    templates_dir: Path,
) -> Tuple[DailyReport, str, str, str]:
    """Stage 5: Synthesize and render HTML report, HTML email, and text email."""
    report_payload = build_daily_report_payload(
        domain_id=domain_cfg.id,
        domain_name=domain_cfg.name,
        report_date=report_date,
        ranked_developments=ranked_developments,
        total_articles_monitored=total_articles,
    )
    html_report = render_html_report(report_payload, templates_dir)
    report_url = f"https://signalbrief.local/reports/daily_brief_{domain_cfg.id}_{report_date}.html"
    email_html = render_email_html(report_payload, report_url, templates_dir)
    email_text = render_email_text(report_payload, report_url, templates_dir)

    return report_payload, html_report, email_html, email_text
