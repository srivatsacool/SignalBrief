# Cloudflare D1 Data Dictionary

This document details the relational schemas and table purposes in SignalBrief's D1 SQLite database.

## Tables Summary

| Table | Description |
| :--- | :--- |
| `users` | Subscriber profiles, timezones, and account statuses (up to 10 invited subscribers). |
| `domains` | Catalog of monitored subject areas (e.g. Manufacturing, Supply Chain). |
| `user_preferences` | User-selected domains, customized keywords, and delivery schedules. |
| `sources` | Approved registry of RSS feeds and public endpoints with polling rules. |
| `articles` | Normalized article metadata, canonical URLs, content hashes, and extracted text. |
| `article_analysis` | NLP extractions, relevance scores, sentiment scores, and topic cluster IDs. |
| `topics` | Clustered themes and topic labels generated for each daily run. |
| `reports` | Daily intelligence brief records, executive summaries, and Cloudflare R2 storage keys. |
| `report_articles` | Mapping of articles linked as citations in each generated report. |
| `email_logs` | Audit trail of email delivery attempts, timestamps, and error responses. |
| `pipeline_runs` | Performance tracking, counts, execution runtimes, and health metrics. |
