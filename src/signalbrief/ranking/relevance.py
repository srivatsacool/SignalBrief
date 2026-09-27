"""Relevance scoring based on domain keywords and subtopic matching."""

import math
from typing import List, Optional


def compute_relevance_score(
    text: str,
    keywords: List[str],
    subtopics: List[str],
    entity_names: Optional[List[str]] = None,
) -> float:
    """Compute keyword and domain relevance score in [0.0, 1.0]."""
    text_lower = text.lower()
    kw_hits = sum(1.5 if " " in kw else 1.0 for kw in keywords if kw.lower() in text_lower)
    sub_hits = sum(1.2 if " " in sub else 1.0 for sub in subtopics if sub.lower() in text_lower)

    entity_hits = 0
    if entity_names:
        entity_hits = sum(1.0 for ent in entity_names if ent.lower() in text_lower)

    raw_score = (kw_hits * 0.5) + (sub_hits * 0.35) + (entity_hits * 0.15)
    # Sigmoidal scaling to [0, 1]
    scaled = 1.0 / (1.0 + math.exp(-0.8 * (raw_score - 2.0)))
    return round(float(scaled), 3)
