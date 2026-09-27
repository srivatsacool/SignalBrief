"""Default configurations and constants for SignalBrief."""

from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "configs"
DOMAINS_DIR = CONFIG_DIR / "domains"
SOURCES_DIR = CONFIG_DIR / "sources"
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

DEFAULT_DOMAIN_ID = "manufacturing"
