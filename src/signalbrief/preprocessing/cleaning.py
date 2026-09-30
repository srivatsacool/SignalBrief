"""Text extraction, HTML cleaning, whitespace normalization, and journalistic stopword filtering."""

import html
import re
import unicodedata
from typing import List, Set

from bs4 import BeautifulSoup

JOURNALISTIC_STOPWORDS: Set[str] = {
    "said", "says", "announced", "announces", "reported", "reporting", "according", "also",
    "new", "year", "years", "month", "months", "week", "weeks", "day", "days", "today", "yesterday",
    "wednesday", "thursday", "friday", "monday", "tuesday", "saturday", "sunday",
    "inc", "corp", "co", "llc", "ltd", "september", "august", "july", "october",
    "update", "updates", "statement", "release", "press", "news", "facility", "facilities",
    "download", "brief", "digest", "daily", "high", "reporters", "spokesperson",
}


def normalize_whitespace(text: str) -> str:
    """Normalize repeated whitespace, tabs, and newlines to a single space."""
    return re.sub(r"\s+", " ", text).strip()


def strip_html_tags(html_content: str) -> str:
    """Safely strip HTML tags, script blocks, and style blocks using BeautifulSoup."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for script_or_style in soup(["script", "style", "nav", "footer", "aside"]):
        script_or_style.extract()
    raw = soup.get_text(separator=" ")
    # Fix detached punctuation like "word ." -> "word."
    cleaned = re.sub(r"\s+([.,;:!?])", r"\1", raw)
    return normalize_whitespace(cleaned)


def clean_article_text(raw_text: str) -> str:
    """Clean and normalize raw text by stripping HTML, unescaping entities, and normalizing whitespace."""
    if not raw_text:
        return ""
    # Strip HTML tags
    stripped = strip_html_tags(raw_text)
    # Unescape HTML entities (&amp; -> &, &#8217; -> ', etc.)
    unescaped = html.unescape(stripped)
    # Normalize curly smart quotes and dashes to standard ASCII
    unescaped = re.sub(r"[\u201c\u201d]", '"', unescaped)
    unescaped = re.sub(r"[\u2018\u2019]", "'", unescaped)
    unescaped = re.sub(r"[\u2013\u2014]", "-", unescaped)
    # Normalize unicode characters (NFKD)
    normalized_unicode = unicodedata.normalize("NFKD", unescaped)
    # Remove multiple spaces and newlines
    normalized = normalize_whitespace(normalized_unicode)
    return normalized


def count_words(text: str) -> int:
    """Return the total word count of a clean text string."""
    return len(re.findall(r"\b\w+\b", text))


def filter_journalistic_stopwords(tokens: List[str]) -> List[str]:
    """Filter out journalistic noise tokens from keywords and topic labels."""
    return [t for t in tokens if t.lower() not in JOURNALISTIC_STOPWORDS and len(t) > 2]
