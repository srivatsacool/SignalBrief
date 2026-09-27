"""Named entity recognition and domain entity extraction."""

import re
from typing import Dict, List, Set

KNOWN_ORGANIZATIONS = {
    "NIST", "Amazon", "US Steel", "Pirelli", "USPS", "MIT", "SME", "Siemens",
    "Rockwell Automation", "ABB", "FANUC", "KUKA", "Boeing", "Lockheed", "Department of Defense",
    "Pentagon", "Eli Lilly", "General Motors", "Ford", "Tesla", "Intel", "TSMC"
}

KNOWN_TECHNOLOGIES = {
    "AI", "Artificial Intelligence", "Robotics", "AGV", "AMR", "CNC", "3D Printing",
    "Additive Manufacturing", "Computer Vision", "Predictive Maintenance", "IoT",
    "Digital Twin", "Cybersecurity", "MEP", "LLM", "Semiconductor"
}


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named organizations, technologies, and dollar amounts from text."""
    found_orgs: Set[str] = set()
    found_tech: Set[str] = set()
    found_metrics: List[str] = []

    # Check known organizations
    for org in KNOWN_ORGANIZATIONS:
        # Match as whole word case-insensitively or strictly
        pattern = r"\b" + re.escape(org) + r"\b"
        if re.search(pattern, text, re.IGNORECASE if len(org) > 4 else 0):
            found_orgs.add(org)

    # Check known technologies
    for tech in KNOWN_TECHNOLOGIES:
        pattern = r"\b" + re.escape(tech) + r"\b"
        if re.search(pattern, text, re.IGNORECASE if len(tech) > 4 else 0):
            found_tech.add(tech)

    # Extract monetary figures and metrics (e.g. $1.7 Million, $30 Million, 40%)
    money_matches = re.findall(r"\$[\d,]+(?:\.\d+)?\s*(?:million|billion|trillion|k|M|B)?", text, re.IGNORECASE)
    percent_matches = re.findall(r"\d+(?:\.\d+)?%", text)
    found_metrics = list(set(money_matches + percent_matches))

    return {
        "organizations": sorted(list(found_orgs)),
        "technologies": sorted(list(found_tech)),
        "metrics": sorted(found_metrics),
    }
