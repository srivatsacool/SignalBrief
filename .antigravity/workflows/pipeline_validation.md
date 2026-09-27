# Pipeline Validation Workflow

This workflow specifies how to validate the end-to-end data pipeline before transitioning from notebooks to production modules and deployment.

## Validation Gates

### Gate 1: Source Ingestion & Resiliency
- Feed fetch failures, timeouts, and HTTP error codes (403, 404, 429, 500) must be handled gracefully without terminating the pipeline.
- Articles without publish dates or with invalid formats fallback to fetch timestamps.
- Canonical URL normalization and content hashing must prevent duplicate records.

### Gate 2: Preprocessing & Data Cleaning
- HTML tags, scripts, tracking params, and boilerplate are scrubbed.
- Articles in unsupported languages are cleanly detected and flagged/filtered.
- Missing titles or empty article bodies trigger validation errors and are logged.

### Gate 3: NLP & Analytical Quality
- Keyword matching and domain classification are deterministic.
- Gold-standard benchmark evaluation is executed against `data/evaluation/` fixtures.
- Sentiment scoring and entity extraction produce valid structured schemas.

### Gate 4: Relevance & Deduplication
- Scoring combines keyword relevance, domain match, and publication recency.
- Similar stories are grouped into topic clusters so a single event does not dominate the briefing.

### Gate 5: Report Generation & Verification
- AI summaries must be strictly traceable to source article facts (evidence validation).
- Rendered HTML report is fully responsive, valid HTML5, and passes inline CSS email formatting checks.
- Generating a report twice for the same date/domain is completely idempotent.
