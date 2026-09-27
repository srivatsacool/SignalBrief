"""Base classes and data models for article collection."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class RawArticle(BaseModel):
    """Raw article data captured from public sources."""
    id: str
    source_id: str
    domain_id: str
    title: str
    url: str
    url_canonical: Optional[str] = None
    content_hash: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary_raw: Optional[str] = None
    content_raw: Optional[str] = None
