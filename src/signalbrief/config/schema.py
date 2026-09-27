"""Configuration data schemas for SignalBrief using Pydantic."""

from typing import List, Optional

from pydantic import BaseModel, Field


class DomainReportConfig(BaseModel):
    max_developments: int = Field(default=5, ge=1, le=10)
    include_sentiment: bool = True
    include_trends: bool = True


class DomainConfig(BaseModel):
    id: str
    name: str
    description: str
    keywords: List[str] = Field(default_factory=list)
    subtopics: List[str] = Field(default_factory=list)
    excluded_keywords: List[str] = Field(default_factory=list)
    report: DomainReportConfig = Field(default_factory=DomainReportConfig)


class SourceConfig(BaseModel):
    id: str
    name: str
    domain_id: str
    url: str
    feed_url: str
    source_type: str = "rss"
    permitted_method: str = "rss_fetch"
    polling_frequency_minutes: int = 360
    active: bool = True
    reliability_score: float = Field(default=0.85, ge=0.0, le=1.0)
    notes: Optional[str] = None

    @property
    def endpoint(self) -> str:
        return self.feed_url or self.url



class SourcesListConfig(BaseModel):
    sources: List[SourceConfig] = Field(default_factory=list)


class CollectionPipelineConfig(BaseModel):
    lookback_hours: int = 48
    max_articles_per_source: int = 30
    request_timeout_seconds: int = 15
    user_agent: str = "SignalBrief/1.0"
    max_concurrent_requests: int = 5
    retry_attempts: int = 2
    retry_backoff_seconds: int = 3


class PreprocessingPipelineConfig(BaseModel):
    min_article_length_words: int = 40
    max_article_length_words: int = 5000
    supported_languages: List[str] = Field(default_factory=lambda: ["en"])
    strip_html_boilerplate: bool = True
    similarity_dedup_threshold: float = 0.85


class AnalyticsPipelineConfig(BaseModel):
    min_relevance_score: float = 0.35
    max_clusters: int = 8
    cluster_similarity_threshold: float = 0.65
    max_developments_per_report: int = 5
    sentiment_analysis_enabled: bool = True
    entity_extraction_enabled: bool = True


class ReportingPipelineConfig(BaseModel):
    format: str = "html"
    template_path: str = "templates/reports/daily_report.html.jinja2"
    include_evidence_links: bool = True
    include_sentiment_badge: bool = True
    max_bullet_points_per_item: int = 3


class PipelineConfig(BaseModel):
    name: str = "SignalBrief Daily Intelligence Pipeline"
    version: str = "1.0.0"
    environment: str = "development"
    collection: CollectionPipelineConfig = Field(default_factory=CollectionPipelineConfig)
    preprocessing: PreprocessingPipelineConfig = Field(default_factory=PreprocessingPipelineConfig)
    analytics: AnalyticsPipelineConfig = Field(default_factory=AnalyticsPipelineConfig)
    reporting: ReportingPipelineConfig = Field(default_factory=ReportingPipelineConfig)
