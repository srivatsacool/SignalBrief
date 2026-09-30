"""Data models for generated intelligence briefs, citations, and analytical frameworks."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    article_id: str
    source_name: str
    title: str
    url: str


class ReportDevelopment(BaseModel):
    id: str
    headline: str
    what_changed: str
    why_it_matters: str
    business_implications: str = ""
    what_to_watch: str
    topic_label: Optional[str] = None
    event_type: Optional[str] = None
    key_entities: Dict[str, List[str]] = Field(default_factory=dict)
    sources: List[Citation] = Field(default_factory=list)
    relevance_score: float = 0.0

    @property
    def title(self) -> str:
        return self.headline

    @property
    def what_happened(self) -> str:
        return self.what_changed


# Alias for backward/forward blueprint compatibility
DevelopmentItem = ReportDevelopment


class DailyReport(BaseModel):
    id: str
    user_id: Optional[str] = None
    domain_id: str
    domain_name: str
    report_date: str
    executive_summary: str
    developments: List[ReportDevelopment] = Field(default_factory=list)
    what_to_watch_next: List[str] = Field(default_factory=list)
    article_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dashboard_url: str = "https://signalbrief.local"
    unsubscribe_url: str = "https://signalbrief.local/settings"

    @property
    def executive_takeaway(self) -> str:
        return self.executive_summary
