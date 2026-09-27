"""Article validation models and sanity checks."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from signalbrief.preprocessing.cleaning import clean_article_text, count_words
from signalbrief.preprocessing.language import is_supported_language


class CleanArticle(BaseModel):
    """Cleaned, validated, and normalized article ready for NLP analysis."""
    id: str
    source_id: str
    domain_id: str
    title: str
    url: str
    url_canonical: str
    content_hash: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    clean_text: str
    word_count: int
    language: str = "en"
    is_valid: bool = True
    validation_notes: Optional[str] = None


def validate_and_clean_article(
    raw_article,
    min_words: int = 20,
    max_words: int = 10000,
    supported_languages: Optional[list] = None,
) -> Optional[CleanArticle]:
    """Transform a RawArticle into a CleanArticle, applying sanity rules."""
    text_source = raw_article.content_raw or raw_article.summary_raw or ""
    clean_text = clean_article_text(text_source)
    words = count_words(clean_text)

    if words < min_words:
        return None

    if not is_supported_language(clean_text, supported_languages):
        return None

    return CleanArticle(
        id=raw_article.id,
        source_id=raw_article.source_id,
        domain_id=raw_article.domain_id,
        title=raw_article.title.strip(),
        url=raw_article.url,
        url_canonical=raw_article.url_canonical or raw_article.url,
        content_hash=raw_article.content_hash,
        author=raw_article.author,
        published_at=raw_article.published_at,
        fetched_at=raw_article.fetched_at,
        clean_text=clean_text,
        word_count=words,
        language="en",
        is_valid=True,
    )
