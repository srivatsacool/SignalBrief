-- SignalBrief Migration 0002: Pipeline Job Lifecycle Tracking
-- Adds pipeline_jobs table for real async job status (replaces simulated telemetry)

-- Job lifecycle: QUEUED -> RUNNING -> COMPLETED | FAILED | PARTIAL
CREATE TABLE IF NOT EXISTS pipeline_jobs (
    id TEXT PRIMARY KEY,
    domain_id TEXT NOT NULL,
    run_date DATE NOT NULL,
    status TEXT CHECK(status IN ('queued','running','completed','failed','partial')) DEFAULT 'queued',
    triggered_by TEXT DEFAULT 'user',
    job_token TEXT,
    sources_total INTEGER DEFAULT 0,
    articles_collected INTEGER DEFAULT 0,
    articles_processed INTEGER DEFAULT 0,
    relevant_articles INTEGER DEFAULT 0,
    clusters_formed INTEGER DEFAULT 0,
    report_id TEXT,
    error_message TEXT,
    queued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY(domain_id) REFERENCES domains(id)
);
CREATE INDEX IF NOT EXISTS idx_jobs_domain_date ON pipeline_jobs(domain_id, run_date);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON pipeline_jobs(status);
