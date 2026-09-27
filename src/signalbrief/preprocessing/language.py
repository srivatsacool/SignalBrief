"""Language detection and filtering."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """Detect language code (e.g. 'en', 'fr') using langdetect or fallback to 'en'."""
    if not text or len(text.strip()) < 20:
        return "unknown"
    try:
        from langdetect import detect
        return detect(text)
    except Exception as e:
        logger.debug(f"Language detection failed: {e}")
        return "en"


def is_supported_language(text: str, supported: Optional[list] = None) -> bool:
    """Verify if the text language is within the supported list (default: ['en'])."""
    valid = supported or ["en"]
    lang = detect_language(text)
    return lang in valid
