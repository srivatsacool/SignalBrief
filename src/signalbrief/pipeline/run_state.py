"""Pipeline run state machine and execution tracking."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    PENDING = "pending"
    COLLECTING = "collecting"
    ANALYSING = "analysing"
    GENERATING = "generating"
    ARCHIVED = "archived"
    DELIVERED = "delivered"
    PARTIAL = "partial"
    RETRYING = "retrying"
    FAILED = "failed"


class RunState(BaseModel):
    """Execution state machine record for a daily pipeline run."""
    run_id: str
    domain_id: str
    run_date: str
    status: PipelineStatus = PipelineStatus.PENDING
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    articles_collected: int = 0
    articles_processed: int = 0
    relevant_articles: int = 0
    clusters_formed: int = 0
    reports_generated: int = 0
    emails_delivered: int = 0
    report_id: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def duration_seconds(self) -> float:
        """Elapsed seconds since pipeline start."""
        end = self.completed_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds()

    def transition_to(self, new_status: PipelineStatus, error: Optional[str] = None):
        """Transition pipeline state safely."""
        self.status = new_status
        if error:
            self.error_message = error
        if new_status in {PipelineStatus.DELIVERED, PipelineStatus.FAILED}:
            self.completed_at = datetime.now(timezone.utc)
