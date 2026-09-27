"""Subtopic classification for domain articles using keyword and taxonomy matching."""

from typing import Dict, List, Tuple

DEFAULT_SUBTOPIC_TAXONOMY = {
    "industrial AI": [
        "ai", "artificial intelligence", "machine learning", "computer vision",
        "deep learning", "neural network", "generative ai", "llm"
    ],
    "predictive maintenance": [
        "predictive maintenance", "condition monitoring", "vibration analysis",
        "sensor data", "equipment failure", "downtime", "maintenance"
    ],
    "production technology": [
        "production technology", "automation", "robotics", "robot", "agv",
        "additive manufacturing", "3d printing", "cnc", "smart factory", "facility"
    ],
    "supply chain resilience": [
        "supply chain", "logistics", "procurement", "freight", "shipping",
        "port", "warehouse", "inventory", "delays", "nearshoring"
    ],
    "workforce analytics": [
        "workforce", "apprenticeship", "internship", "hiring", "talent",
        "training", "stem", "jobs", "labor", "workforce development"
    ],
    "standards & governance": [
        "standard", "standards", "nist", "cybersecurity", "mep", "compliance",
        "regulation", "award", "grant", "funding", "guidelines"
    ],
}


def classify_subtopic(
    text: str,
    subtopics_dict: Dict[str, List[str]] = None,
    default_label: str = "general manufacturing",
) -> Tuple[str, float]:
    """Classify text into a subtopic based on taxonomy term matching and frequency.

    Returns (predicted_subtopic, confidence_score).
    """
    taxonomy = subtopics_dict or DEFAULT_SUBTOPIC_TAXONOMY
    text_lower = text.lower()

    scores = {}
    for subtopic, terms in taxonomy.items():
        score = 0
        for term in terms:
            if term in text_lower:
                # Count occurrences of term
                occurrences = text_lower.count(term)
                # Weight longer multi-word phrases higher
                weight = 1.5 if " " in term else 1.0
                score += occurrences * weight
        scores[subtopic] = score

    best_subtopic, best_score = max(scores.items(), key=lambda x: x[1])
    total_score = sum(scores.values())

    if best_score == 0 or total_score == 0:
        return default_label, 0.0

    confidence = round(best_score / total_score, 2)
    return best_subtopic, confidence
