# SignalBrief System Architecture Overview

SignalBrief is an open-source, free-first, notebook-first AI text analytics and daily intelligence briefing platform.

## Core Architectural Blueprint

```mermaid
flowchart TD
    subgraph Ingestion ["1. Multi-Source Ingestion"]
        RSS["Public RSS Feeds (NIST, Tech Dives, Robot Report)"]
        APIs["Public REST APIs"]
        Collector["signalbrief.collectors (RSS/API/Scheduler)"]
        Dedup["Canonical Normalizer & SHA-256 Dedup"]
        RSS --> Collector
        APIs --> Collector
        Collector --> Dedup
    end

    subgraph Processing ["2. Text Preprocessing & Validation"]
        Cleaner["HTML Stripper & Entity Unescaper"]
        LangFilter["Language Filter (en) & Bounds Validator"]
        Dedup --> Cleaner --> LangFilter
    end

    subgraph Analytics ["3. NLP Analytics & Taxonomy"]
        Classify["Subtopic Classifier (Whole-Word Boundary)"]
        NER["Named Entity Recognition (Orgs, Agencies, Tech)"]
        Sentiment["Industrial Tone Polarity"]
        LangFilter --> Classify
        LangFilter --> NER
        LangFilter --> Sentiment
    end

    subgraph Clustering ["4. Topic Clustering & Ranking"]
        TFIDF["TF-IDF Vector Space"]
        AggClust["Agglomerative Cosine Clustering"]
        Centroid["Centroid Discovery & Thematic Labeling"]
        Ranker["Multi-Factor Scoring (Relevance, Recency, Multi-Source)"]
        Classify & NER & Sentiment --> TFIDF --> AggClust --> Centroid --> Ranker
    end

    subgraph Synthesis ["5. Triadic Synthesis & Multi-Format Rendering"]
        Triad["Triadic Formulator (What Changed, Why It Matters, What To Watch)"]
        Validator["Editorial & 100% Citation Coverage Validator"]
        HTMLReport["Responsive HTML Report"]
        EmailTpl["Mobile-Optimized HTML & Plaintext Email"]
        Ranker --> Triad --> Validator --> HTMLReport & EmailTpl
    end

    subgraph Cloudflare ["6. Cloudflare Serverless Backend"]
        WorkersCron["Cloudflare Workers (0 2 * * * Cron)"]
        Queues["Pipeline Queue & DLQ"]
        D1["Cloudflare D1 (SQLite Metadata & Subscriptions)"]
        R2["Cloudflare R2 (HTML Report Archive)"]
        WorkersAI["Workers AI (@cf/meta/llama-3-8b-instruct)"]
        Pages["Cloudflare Pages (Astro + React Dashboard)"]
        WorkersCron --> Queues --> WorkersAI
        WorkersAI --> D1 & R2
        D1 & R2 --> Pages
    end
```

## Architectural Tenets

1. **Notebook-First Research**: All empirical methods and algorithms were researched, evaluated, and documented in notebooks `00` through `10` before migration to production modules.
2. **Zero-Paid Dependency**: The entire stack operates reliably within free tier limits (Cloudflare Workers, D1, R2, GitHub Actions, open-source models).
3. **100% Citation Coverage**: Every development reported in a briefing must link directly to verified public primary sources.
4. **Clean Decoupling**: Reusable Python analytical logic in `src/signalbrief/` executes standalone via CLI (`signalbrief run`) or within scheduled Cloudflare serverless environments.
