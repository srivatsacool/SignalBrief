"""Loaders for YAML configuration files into validated Pydantic models."""

from pathlib import Path
from typing import List, Optional

import yaml

from signalbrief.config.defaults import (
    CONFIG_DIR,
    DOMAINS_DIR,
    SOURCES_DIR,
)
from signalbrief.config.schema import (
    DomainConfig,
    PipelineConfig,
    SourceConfig,
    SourcesListConfig,
)


def load_yaml(file_path: Path) -> dict:
    """Safely load a YAML file and return a dictionary."""
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_pipeline_config(config_path: Optional[Path] = None) -> PipelineConfig:
    """Load the global pipeline configuration."""
    path = config_path or (CONFIG_DIR / "pipeline.yaml")
    raw_data = load_yaml(path)
    return PipelineConfig(**raw_data.get("pipeline", raw_data))


def load_domain_config(domain_id: str, domains_dir: Optional[Path] = None) -> DomainConfig:
    """Load a specific domain configuration by its identifier."""
    directory = domains_dir or DOMAINS_DIR
    target_path = directory / f"{domain_id}.yaml"
    raw_data = load_yaml(target_path)
    domain_data = raw_data.get("domain", raw_data)
    return DomainConfig(**domain_data)


def load_sources_for_domain(domain_id: str, sources_dir: Optional[Path] = None) -> List[SourceConfig]:
    """Load all configured sources for a given domain."""
    directory = sources_dir or SOURCES_DIR
    sources: List[SourceConfig] = []

    # Check domain-specific source file first
    domain_source_file = directory / f"{domain_id}.yaml"
    if domain_source_file.exists():
        raw_data = load_yaml(domain_source_file)
        parsed = SourcesListConfig(**raw_data)
        sources.extend(parsed.sources)

    # Check general sources file as well
    general_source_file = directory / "general.yaml"
    if general_source_file.exists():
        raw_data = load_yaml(general_source_file)
        parsed = SourcesListConfig(**raw_data)
        # Filter for active sources that match or apply generally
        for src in parsed.sources:
            if src.active and (src.domain_id == domain_id or src.domain_id == "general"):
                sources.append(src)

    return sources


def list_available_domains(domains_dir: Optional[Path] = None) -> List[str]:
    """List IDs of all available domains configured in configs/domains/."""
    directory = domains_dir or DOMAINS_DIR
    if not directory.exists():
        return []
    return [p.stem for p in directory.glob("*.yaml")]
