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
| `reports` | Daily intelligence brief records, headlines, executive summaries, and Cloudflare R2 storage keys. |
| `report_articles` | Mapping of articles linked in each generated report (legacy junction). |
| `report_developments` | Structured triadic developments (headline, what changed, why it matters, what to watch) for each brief. |
| `report_sources` | Traceable source citations linked to each report development with titles and URLs. |
| `delivery_logs` | Audit trail of email delivery attempts, status, provider message IDs, timestamps, and error responses. |
| `email_logs` | Backward compatibility view exposing legacy fields from `delivery_logs`. |
| `pipeline_runs` | Performance tracking, counts, execution runtimes, and health metrics. |
