"""Text extraction, HTML cleaning, and whitespace normalization."""

import html
import re
import unicodedata

from bs4 import BeautifulSoup


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
