"""Text extraction, HTML cleaning, and whitespace normalization."""

import re

from bs4 import BeautifulSoup


def strip_html_tags(html_content: str) -> str:
    """Safely strip HTML tags, script blocks, and style blocks using BeautifulSoup."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for script_or_style in soup(["script", "style", "nav", "footer", "aside"]):
        script_or_style.extract()
    return soup.get_text(separator=" ")


def clean_article_text(raw_text: str) -> str:
    """Clean and normalize raw text by stripping HTML, entities, and whitespace."""
    if not raw_text:
        return ""
    stripped = strip_html_tags(raw_text)
    # Remove multiple spaces and newlines
    normalized = re.sub(r"\s+", " ", stripped).strip()
    return normalized


def count_words(text: str) -> int:
    """Return the total word count of a clean text string."""
    return len(re.findall(r"\b\w+\b", text))
