"""Text and structural extraction utilities for raw articles."""

import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup


def extract_lead_paragraph(text: str, max_words: int = 60) -> str:
    """Extract the first substantial paragraph or lead sentence from text."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    if not paragraphs:
        return ""

    lead = paragraphs[0]
    words = lead.split()
    if len(words) > max_words:
        lead = " ".join(words[:max_words]) + "..."
    return lead


def extract_numeric_metrics(text: str) -> List[Dict[str, str]]:
    """Extract financial, percentage, and production metrics from text."""
    patterns = [
        (r"\$\s?(\d+(?:\.\d+)?\s?(?:billion|million|trillion|B|M|k)?)", "currency"),
        (r"(\d+(?:\.\d+)?\s?%)", "percentage"),
        (r"(\d{1,3}(?:,\d{3})+|\d+)\s*(?:units|tons|megawatts|sq ft|facilities|workers|jobs)", "production_metric"),
    ]
    extracted = []
    for pattern, m_type in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            extracted.append({
                "value": match.group(0).strip(),
                "type": m_type,
            })
    return extracted


def extract_html_metadata(html_content: str) -> Dict[str, Optional[str]]:
    """Extract metadata (title, author, published date, canonical url) from raw HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    metadata: Dict[str, Optional[str]] = {
        "title": None,
        "author": None,
        "published_at": None,
        "canonical_url": None,
    }

    if soup.title:
        metadata["title"] = soup.title.get_text(strip=True)

    canon = soup.find("link", rel="canonical")
    if canon and canon.get("href"):
        metadata["canonical_url"] = canon["href"].strip()

    author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
    if author_meta and author_meta.get("content"):
        metadata["author"] = author_meta["content"].strip()

    time_meta = soup.find("meta", property="article:published_time") or soup.find("time", attrs={"datetime": True})
    if time_meta:
        metadata["published_at"] = time_meta.get("content") or time_meta.get("datetime")

    return metadata


def split_sentences(text: str) -> List[str]:
    """Split text into sentences while respecting common abbreviations."""
    # Simple regex sentence splitter
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 5]
