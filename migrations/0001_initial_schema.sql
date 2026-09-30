-- SignalBrief Initial Schema Migration
-- Migration: 0001_initial_schema.sql
-- Target: Cloudflare D1 (SQLite compatible)

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    timezone TEXT DEFAULT 'UTC',
    status TEXT CHECK(status IN ('active', 'paused', 'invited', 'deleted')) DEFAULT 'invited',
    is_admin INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Domains
CREATE TABLE IF NOT EXISTS domains (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. User Preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    custom_keywords TEXT, -- JSON array of strings
    delivery_time_utc TEXT DEFAULT '06:00',
    email_enabled INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    UNIQUE(user_id, domain_id)
);

-- 4. Sources
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    url TEXT NOT NULL,
    feed_url TEXT NOT NULL,
    source_type TEXT CHECK(source_type IN ('rss', 'api', 'webpage')) DEFAULT 'rss',
    permitted_method TEXT DEFAULT 'rss_fetch',
    polling_frequency_minutes INTEGER DEFAULT 360,
    active INTEGER DEFAULT 1,
    reliability_score REAL DEFAULT 0.85,
    last_polled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(domain_id) REFERENCES domains(id)
);

-- 5. Articles
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    url_canonical TEXT,
    content_hash TEXT NOT NULL,
    author TEXT,
    published_at DATETIME,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    summary_text TEXT,
    clean_text TEXT,
    language TEXT DEFAULT 'en',
    word_count INTEGER,
    FOREIGN KEY(source_id) REFERENCES sources(id),
    FOREIGN KEY(domain_id) REFERENCES domains(id)
);
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(content_hash);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);

-- 6. Topics
CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    domain_id TEXT NOT NULL,
    label TEXT NOT NULL,
    keywords TEXT, -- JSON array
    cluster_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(domain_id) REFERENCES domains(id)
);

-- 7. Article Analysis
CREATE TABLE IF NOT EXISTS article_analysis (
    article_id TEXT PRIMARY KEY,
    topic_id TEXT,
    relevance_score REAL DEFAULT 0.0,
    novelty_score REAL DEFAULT 0.0,
    sentiment_label TEXT CHECK(sentiment_label IN ('positive', 'neutral', 'negative')),
    sentiment_score REAL DEFAULT 0.0,
    entities TEXT, -- JSON array of extracted entities
    keywords TEXT, -- JSON array of top TF-IDF keywords
    analysed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY(topic_id) REFERENCES topics(id)
);
CREATE INDEX IF NOT EXISTS idx_analysis_relevance ON article_analysis(relevance_score);

-- 8. Reports
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    user_id TEXT, -- NULL for shared domain-level report
    domain_id TEXT NOT NULL,
    report_date DATE NOT NULL,
    headline TEXT,
    status TEXT CHECK(status IN ('pending', 'collecting', 'analysing', 'generating', 'archived', 'delivered', 'failed')) DEFAULT 'pending',
    r2_key TEXT NOT NULL,
    article_count INTEGER DEFAULT 0,
    executive_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(domain_id) REFERENCES domains(id),
    UNIQUE(user_id, domain_id, report_date)
);
CREATE INDEX IF NOT EXISTS idx_reports_lookup ON reports(user_id, domain_id, report_date);

-- 9. Report Articles
CREATE TABLE IF NOT EXISTS report_articles (
    report_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    cluster_rank INTEGER,
    PRIMARY KEY(report_id, article_id),
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY(article_id) REFERENCES articles(id)
);

-- 10. Report Developments
CREATE TABLE IF NOT EXISTS report_developments (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL,
    headline TEXT NOT NULL,
    what_changed TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    what_to_watch TEXT NOT NULL,
    topic_label TEXT,
    relevance_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_devs_report ON report_developments(report_id);

-- 11. Report Sources
CREATE TABLE IF NOT EXISTS report_sources (
    id TEXT PRIMARY KEY,
    development_id TEXT NOT NULL,
    article_id TEXT,
    source_name TEXT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(development_id) REFERENCES report_developments(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sources_dev ON report_sources(development_id);

-- 12. Delivery Logs
CREATE TABLE IF NOT EXISTS delivery_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    report_id TEXT NOT NULL,
    recipient_email TEXT NOT NULL,
    delivery_status TEXT CHECK(delivery_status IN ('pending', 'sent', 'delivered', 'failed', 'retrying')) DEFAULT 'pending',
    provider_message_id TEXT,
    error_message TEXT,
    delivered_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(report_id) REFERENCES reports(id)
);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_report ON delivery_logs(report_id);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_user ON delivery_logs(user_id);

-- Backward compatibility view for legacy email_logs references
CREATE VIEW IF NOT EXISTS email_logs AS
SELECT 
    id,
    report_id,
    user_id,
    recipient_email,
    delivery_status AS status,
    0 AS attempt_count,
    error_message,
    delivered_at AS sent_at,
    created_at
FROM delivery_logs;

-- 13. Pipeline Runs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY,
    domain_id TEXT NOT NULL,
    run_date DATE NOT NULL,
    status TEXT CHECK(status IN ('started', 'completed', 'partial', 'failed')) DEFAULT 'started',
    articles_collected INTEGER DEFAULT 0,
    articles_processed INTEGER DEFAULT 0,
    reports_generated INTEGER DEFAULT 0,
    emails_sent INTEGER DEFAULT 0,
    error_log TEXT,
    duration_seconds REAL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY(domain_id) REFERENCES domains(id)
);
