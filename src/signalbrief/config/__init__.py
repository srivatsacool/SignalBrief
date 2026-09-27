"""Configuration module for SignalBrief."""

from signalbrief.config.defaults import (
    CONFIG_DIR,
    DATA_DIR,
    DEFAULT_DOMAIN_ID,
    DOMAINS_DIR,
    REPORTS_DIR,
    SOURCES_DIR,
    TEMPLATES_DIR,
)
from signalbrief.config.loader import (
    list_available_domains,
    load_domain_config,
    load_pipeline_config,
    load_sources_for_domain,
)
from signalbrief.config.schema import (
    DomainConfig,
    PipelineConfig,
    SourceConfig,
)

__all__ = [
    "CONFIG_DIR",
    "DOMAINS_DIR",
    "SOURCES_DIR",
    "DATA_DIR",
    "REPORTS_DIR",
    "TEMPLATES_DIR",
    "DEFAULT_DOMAIN_ID",
    "load_domain_config",
    "load_pipeline_config",
    "load_sources_for_domain",
    "list_available_domains",
    "DomainConfig",
    "PipelineConfig",
    "SourceConfig",
]
