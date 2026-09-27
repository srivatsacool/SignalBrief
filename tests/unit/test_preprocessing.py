"""Unit tests for text preprocessing, HTML cleaning, extraction, and validation."""

from signalbrief.preprocessing.cleaning import clean_article_text, count_words, strip_html_tags
from signalbrief.preprocessing.extraction import (
    extract_lead_paragraph,
    extract_numeric_metrics,
    split_sentences,
)
from signalbrief.preprocessing.language import detect_language
from signalbrief.preprocessing.validation import CleanArticle


def test_strip_html_tags():
    """Verify HTML markup and unwanted script/style tags are removed."""
    raw_html = "<div><p>Manufacturing is <b>modernizing</b>.</p><script>alert('xss');</script></div>"
    clean = strip_html_tags(raw_html)
    assert "Manufacturing is modernizing." in clean
    assert "alert" not in clean


def test_clean_article_text():
    """Verify full pipeline: HTML stripping, entity unescaping, and unicode norm."""
    dirty_text = "<p>Factory &amp; warehouse &#8220;resilience&#8221; at 100&#176;C.</p>"
    clean = clean_article_text(dirty_text)
    assert clean == 'Factory & warehouse "resilience" at 100°C.'


def test_count_words():
    """Verify word count utility counts alphanumeric tokens."""
    text = "Industrial robots boost production output by twenty percent."
    assert count_words(text) == 8


def test_detect_language():
    """Verify language detection identifying English correctly."""
    english_text = "The department of commerce announced new grants for semiconductor manufacturing facilities."
    assert detect_language(english_text) == "en"


def test_extract_lead_paragraph():
    """Verify extracting the lead paragraph with word limits."""
    multiline = "This is the first lead paragraph.\n\nThis is the second body paragraph."
    lead = extract_lead_paragraph(multiline, max_words=10)
    assert lead == "This is the first lead paragraph."


def test_extract_numeric_metrics():
    """Verify extracting financial, percentage, and production metrics."""
    sample = "The facility secured $450 million in funding to increase capacity by 25% and produce 50,000 units."
    metrics = extract_numeric_metrics(sample)
    assert any("$450 million" in m["value"] for m in metrics)
    assert any("25%" in m["value"] for m in metrics)
    assert any("50,000 units" in m["value"] for m in metrics)


def test_split_sentences():
    """Verify sentence tokenization."""
    text = "Production increased in Q3. Supply chains stabilized. New orders arrived."
    sentences = split_sentences(text)
    assert len(sentences) == 3


def test_clean_article_model():
    """Verify CleanArticle Pydantic schema validation."""
    art = CleanArticle(
        id="test_art_01",
        source_id="nist",
        domain_id="manufacturing",
        title="NIST launches manufacturing grant program",
        url="https://example.com/article",
        url_canonical="https://example.com/article",
        content_hash="abc12345",
        clean_text="NIST announced a major initiative for manufacturing innovation.",
        word_count=8,
        language="en",
    )
    assert art.is_valid is True
    assert art.title == "NIST launches manufacturing grant program"
